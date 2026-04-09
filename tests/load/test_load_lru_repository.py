"""
Load test harness for LRUCache and Repository thread-safety.

Simulates real SDK usage patterns:
- Streaming thread: continuously updates flags/segments
- Polling thread: periodically bulk-replaces flags/segments
- App threads: concurrent flag evaluations (reads)
- Eviction pressure: tests LRU eviction under concurrent load

Monitors for:
- Deadlocks (via timeout detection)
- Incorrect values (data corruption)
- Spurious FLAG_NOT_FOUND (the original bug)
- Performance degradation over time

Usage:
    python tests/load/test_load_lru_repository.py [--duration 3600]
"""

import argparse
import logging
import os
import sys
import threading
import time
import random
import signal
from collections import Counter
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from featureflags.lru_cache import LRUCache
from featureflags.repository import Repository

# Suppress SDK logging noise during load test
# The SDK logger is created in featureflags.util with its own handler
from featureflags.util import log as _sdk_log
_sdk_log.setLevel(logging.CRITICAL)


# ---------------------------------------------------------------------------
# Fake models to simulate FeatureConfig / Segment
# ---------------------------------------------------------------------------

class FakeFlag:
    def __init__(self, feature, version=1):
        self.feature = feature
        self.version = version
        self.rules = []


class FakeSegment:
    def __init__(self, identifier, version=1):
        self.identifier = identifier
        self.version = version
        self.serving_rules = []


# ---------------------------------------------------------------------------
# Stats collector (thread-safe)
# ---------------------------------------------------------------------------

@dataclass
class Stats:
    lock: threading.Lock = field(default_factory=threading.Lock)
    reads: int = 0
    writes: int = 0
    deletes: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    false_not_found: int = 0
    wrong_value: int = 0
    errors: Counter = field(default_factory=Counter)
    deadlock_detected: bool = False
    # Reservoir sampling: keep max 10K samples to bound memory
    _max_samples: int = 10000
    latencies_us: list = field(default_factory=list)
    _latency_count: int = 0

    def inc(self, attr, n=1):
        with self.lock:
            setattr(self, attr, getattr(self, attr) + n)

    def record_error(self, err_type):
        with self.lock:
            self.errors[err_type] += 1

    def record_latency(self, us):
        with self.lock:
            self._latency_count += 1
            if len(self.latencies_us) < self._max_samples:
                self.latencies_us.append(us)
            else:
                # Reservoir sampling: replace with decreasing probability
                j = random.randint(0, self._latency_count - 1)
                if j < self._max_samples:
                    self.latencies_us[j] = us

    def snapshot(self):
        with self.lock:
            p50 = p99 = 0
            if self.latencies_us:
                s = sorted(self.latencies_us)
                p50 = s[len(s) // 2]
                p99 = s[int(len(s) * 0.99)]
            return {
                'reads': self.reads,
                'writes': self.writes,
                'deletes': self.deletes,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'false_not_found': self.false_not_found,
                'wrong_value': self.wrong_value,
                'errors': dict(self.errors),
                'deadlock': self.deadlock_detected,
                'latency_p50_us': p50,
                'latency_p99_us': p99,
                'samples': self._latency_count,
            }


# ---------------------------------------------------------------------------
# Test 1: Raw LRUCache stress test
# ---------------------------------------------------------------------------

def run_lru_cache_stress(duration_sec, stats, stop_event):
    """
    Hammer LRUCache with concurrent reads, writes, deletes, keys(),
    and len() calls. Verifies no deadlocks or data corruption.
    """
    cache = LRUCache(size=200)
    num_keys = 500  # more keys than cache size to force evictions

    # Pre-populate
    for i in range(200):
        cache.set(f"key-{i}", f"value-{i}")

    def writer():
        while not stop_event.is_set():
            i = random.randint(0, num_keys - 1)
            cache.set(f"key-{i}", f"value-{i}")
            stats.inc('writes')
            time.sleep(random.uniform(0, 0.001))

    def reader():
        while not stop_event.is_set():
            i = random.randint(0, num_keys - 1)
            key = f"key-{i}"
            t0 = time.monotonic()
            try:
                val = cache.get(key)
                elapsed_us = (time.monotonic() - t0) * 1_000_000
                stats.record_latency(elapsed_us)
                stats.inc('reads')
                if val is not None:
                    stats.inc('cache_hits')
                    if val != f"value-{i}":
                        stats.inc('wrong_value')
                else:
                    stats.inc('cache_misses')
            except Exception as e:
                stats.record_error(type(e).__name__)

    def deleter():
        while not stop_event.is_set():
            i = random.randint(0, num_keys - 1)
            cache.remove([f"key-{i}"])
            stats.inc('deletes')
            time.sleep(random.uniform(0, 0.005))

    def keys_caller():
        while not stop_event.is_set():
            try:
                k = cache.keys()
                length = len(cache)
                _ = (k, length)
            except Exception as e:
                stats.record_error(f"keys:{type(e).__name__}")
            time.sleep(random.uniform(0, 0.002))

    threads = []
    for _ in range(20):
        threads.append(threading.Thread(target=reader, daemon=True))
    for _ in range(5):
        threads.append(threading.Thread(target=writer, daemon=True))
    for _ in range(3):
        threads.append(threading.Thread(target=deleter, daemon=True))
    for _ in range(2):
        threads.append(threading.Thread(target=keys_caller, daemon=True))

    for t in threads:
        t.start()

    deadline = time.monotonic() + duration_sec
    while time.monotonic() < deadline and not stop_event.is_set():
        time.sleep(1)

    stop_event.set()

    for t in threads:
        t.join(timeout=30)
        if t.is_alive():
            stats.deadlock_detected = True


# ---------------------------------------------------------------------------
# Test 2: Repository-level stress test (simulates real SDK)
# ---------------------------------------------------------------------------

def run_repository_stress(duration_sec, stats, stop_event):
    """
    Simulates real SDK patterns:
    - 20 app threads doing get_flag() / get_segment() (reads)
    - 2 streaming threads doing set_flag() / set_segment() (writes)
    - 1 polling thread doing bulk set (periodic full refresh)

    No flag removal thread - all flags remain in cache at all times.
    Any NOT_FOUND result is a genuine false negative (the original bug).
    """
    cache = LRUCache(size=500)
    repo = Repository(cache=cache, store=None)

    num_flags = 50
    num_segments = 30
    flag_ids = [f"flag-{i}" for i in range(num_flags)]
    segment_ids = [f"segment-{i}" for i in range(num_segments)]

    # Pre-populate all flags and segments
    for fid in flag_ids:
        repo.set_flag(FakeFlag(fid, version=1))
    for sid in segment_ids:
        repo.set_segment(FakeSegment(sid, version=1))

    def app_reader():
        """Simulates application threads evaluating flags."""
        while not stop_event.is_set():
            flag_id = random.choice(flag_ids)
            t0 = time.monotonic()
            result = repo.get_flag(flag_id)
            elapsed_us = (time.monotonic() - t0) * 1_000_000
            stats.record_latency(elapsed_us)
            stats.inc('reads')
            if result is not None:
                stats.inc('cache_hits')
            else:
                # Flag should ALWAYS be in cache (never removed)
                # Any None here = the original race condition bug
                stats.inc('false_not_found')

            seg_id = random.choice(segment_ids)
            result = repo.get_segment(seg_id)
            stats.inc('reads')
            if result is not None:
                stats.inc('cache_hits')
            else:
                stats.inc('false_not_found')

    def stream_writer():
        """Simulates streaming thread updating flags (in-place)."""
        version = [2]
        while not stop_event.is_set():
            i = random.randint(0, num_flags - 1)
            flag = FakeFlag(flag_ids[i], version=version[0])
            repo.set_flag(flag)
            stats.inc('writes')
            version[0] += 1
            time.sleep(random.uniform(0.001, 0.01))

            j = random.randint(0, num_segments - 1)
            seg = FakeSegment(segment_ids[j], version=version[0])
            repo.set_segment(seg)
            stats.inc('writes')
            version[0] += 1

    def polling_refresh():
        """Simulates polling thread doing bulk refresh."""
        version = [1000]
        while not stop_event.is_set():
            for fid in flag_ids:
                repo.set_flag(FakeFlag(fid, version=version[0]))
                stats.inc('writes')
                version[0] += 1
            for sid in segment_ids:
                repo.set_segment(FakeSegment(sid, version=version[0]))
                stats.inc('writes')
                version[0] += 1
            time.sleep(random.uniform(2, 5))

    threads = []
    for _ in range(20):
        threads.append(threading.Thread(target=app_reader, daemon=True))
    for _ in range(2):
        threads.append(threading.Thread(target=stream_writer, daemon=True))
    threads.append(threading.Thread(target=polling_refresh, daemon=True))

    for t in threads:
        t.start()

    deadline = time.monotonic() + duration_sec
    while time.monotonic() < deadline and not stop_event.is_set():
        time.sleep(1)

    stop_event.set()

    for t in threads:
        t.join(timeout=30)
        if t.is_alive():
            stats.deadlock_detected = True


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def print_report(name, stats, duration):
    snap = stats.snapshot()
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"  Duration: {duration}s")
    print(f"{'=' * 60}")
    print(f"  Reads:            {snap['reads']:>12,}")
    print(f"  Writes:           {snap['writes']:>12,}")
    print(f"  Deletes:          {snap['deletes']:>12,}")
    print(f"  Cache hits:       {snap['cache_hits']:>12,}")
    print(f"  Cache misses:     {snap['cache_misses']:>12,}")
    print(f"  False NOT_FOUND:  {snap['false_not_found']:>12,}")
    print(f"  Wrong values:     {snap['wrong_value']:>12,}")
    print(f"  Latency p50:      {snap['latency_p50_us']:>9.1f} us")
    print(f"  Latency p99:      {snap['latency_p99_us']:>9.1f} us")
    print(f"  Errors:           {snap['errors'] or 'None'}")
    print(f"  Deadlock:         {snap['deadlock']}")

    passed = (
        snap['false_not_found'] == 0
        and snap['wrong_value'] == 0
        and not snap['errors']
        and not snap['deadlock']
    )
    status = "PASSED" if passed else "FAILED"
    print(f"\n  Result: {status}")
    print(f"{'=' * 60}")
    return passed


def main():
    parser = argparse.ArgumentParser(
        description='Load test for LRUCache and Repository thread-safety'
    )
    parser.add_argument(
        '--duration', type=int, default=3600,
        help='Test duration in seconds (default: 3600 = 1 hour)'
    )
    parser.add_argument(
        '--test', choices=['cache', 'repository', 'both'], default='both',
        help='Which test to run (default: both)'
    )
    args = parser.parse_args()

    duration = args.duration
    half = duration // 2 if args.test == 'both' else duration

    print(f"Load test starting - duration: {duration}s")
    print(f"Press Ctrl+C to stop early\n")

    global_stop = threading.Event()

    def sigint_handler(sig, frame):
        print("\nStopping early...")
        global_stop.set()

    signal.signal(signal.SIGINT, sigint_handler)

    all_passed = True

    if args.test in ('cache', 'both'):
        d = half if args.test == 'both' else duration
        print(f"[1/2] LRUCache stress test ({d}s)...")
        stats1 = Stats()
        stop1 = threading.Event()

        def stop_on_global():
            global_stop.wait()
            stop1.set()

        threading.Thread(target=stop_on_global, daemon=True).start()
        t0 = time.monotonic()
        run_lru_cache_stress(d, stats1, stop1)
        elapsed = time.monotonic() - t0
        p = print_report("LRUCache Stress Test", stats1, int(elapsed))
        all_passed &= p

    if args.test in ('repository', 'both'):
        d = half if args.test == 'both' else duration
        print(f"\n[2/2] Repository stress test ({d}s)...")
        stats2 = Stats()
        stop2 = threading.Event()

        def stop_on_global2():
            global_stop.wait()
            stop2.set()

        threading.Thread(target=stop_on_global2, daemon=True).start()
        t0 = time.monotonic()
        run_repository_stress(d, stats2, stop2)
        elapsed = time.monotonic() - t0
        p = print_report("Repository Stress Test", stats2, int(elapsed))
        all_passed &= p

    print(f"\n{'=' * 60}")
    if all_passed:
        print("  ALL TESTS PASSED - No deadlocks, no data corruption,")
        print("  no false FLAG_NOT_FOUND errors detected.")
    else:
        print("  FAILURES DETECTED - Review results above.")
    print(f"{'=' * 60}\n")

    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
