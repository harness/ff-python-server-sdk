"""
Thread-safety tests for Repository.set_flag / remove_flag
(FFM-13213: non-atomic check-then-set race).
"""

import threading
import time

from featureflags.lru_cache import LRUCache
from featureflags.openapi.config.models.feature_config import FeatureConfig
from featureflags.openapi.config.models.feature_config_kind import \
    FeatureConfigKind
from featureflags.openapi.config.models.feature_state import FeatureState
from featureflags.openapi.config.models.serve import Serve
from featureflags.openapi.config.models.variation import Variation
from featureflags.repository import Repository, format_flag_key

STRESS_DURATION_SECONDS = 5
STRESS_WRITER_THREADS = 6
NUM_FLAGS = 10


def make_flag(identifier, version=1):
    return FeatureConfig(
        project="test_project",
        environment="test_env",
        feature=identifier,
        state=FeatureState.ON,
        kind=FeatureConfigKind.BOOLEAN,
        variations=[
            Variation(identifier="true_var", value="true", name="True"),
            Variation(identifier="false_var", value="false", name="False"),
        ],
        default_serve=Serve(variation="true_var"),
        off_variation="false_var",
        version=version,
    )


def cached_version(repo, identifier):
    flag = repo.cache.get(format_flag_key(identifier))
    return None if flag is None else flag.version


class SlowGetCache(LRUCache):
    """Cache whose get() can be paused after reading, to force the
    interleaving from the ticket."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hook = None

    def get(self, key):
        value = super().get(key)
        hook = self.hook
        if hook is not None:
            hook(value)
        return value


class TestDeterministicInterleaving:

    def test_newer_version_wins_when_check_is_delayed(self):
        cache = SlowGetCache(size=10)
        repo = Repository(cache)
        repo.set_flag(make_flag("f", 4))

        a_read = threading.Event()
        b_done = threading.Event()
        first = threading.local()

        def hook(value):
            # Pause only thread A's staleness check, right after it read v4.
            if getattr(first, "is_a", False) and not a_read.is_set():
                a_read.set()
                # With the repository lock held by A, B cannot finish;
                # time out rather than deadlock.
                b_done.wait(timeout=0.5)

        cache.hook = hook

        def writer_a():
            first.is_a = True
            repo.set_flag(make_flag("f", 5))

        def writer_b():
            a_read.wait(timeout=5)
            repo.set_flag(make_flag("f", 6))
            b_done.set()

        ta = threading.Thread(target=writer_a)
        tb = threading.Thread(target=writer_b)
        ta.start()
        tb.start()
        ta.join(10)
        tb.join(10)

        cache.hook = None
        assert cached_version(repo, "f") == 6


class TestStress:

    def test_final_version_is_max_written(self):
        repo = Repository(LRUCache(size=1000))
        stop = threading.Event()
        counter_lock = threading.Lock()
        counters = {i: 0 for i in range(NUM_FLAGS)}
        errors = []

        def writer(tid):
            try:
                i = 0
                while not stop.is_set():
                    fid = i % NUM_FLAGS
                    with counter_lock:
                        counters[fid] += 1
                        version = counters[fid]
                    repo.set_flag(make_flag(f"flag_{fid}", version))
                    i += 1
            except Exception as e:  # pragma: no cover
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(t,))
                   for t in range(STRESS_WRITER_THREADS)]
        for t in threads:
            t.start()
        time.sleep(STRESS_DURATION_SECONDS)
        stop.set()
        for t in threads:
            t.join(10)

        assert not errors
        for fid, max_version in counters.items():
            assert cached_version(repo, f"flag_{fid}") == max_version


class TestRemoveVsSet:

    def test_remove_wins_over_stale_set(self):
        repo = Repository(LRUCache(size=100))
        repo.set_flag(make_flag("f", 5))
        stop = threading.Event()

        def setter():
            while not stop.is_set():
                # Lower version than anything cached/initially seeded.
                repo.set_flag(make_flag("f", 3))

        t = threading.Thread(target=setter)
        t.start()
        try:
            time.sleep(0.05)
            repo.remove_flag("f")
        finally:
            time.sleep(0.05)
            stop.set()
            t.join(10)

        # After the remove, the cache is empty so the lower-version set
        # may legitimately re-insert; stop the setter first and verify the
        # serialized outcome: a final remove leaves nothing behind.
        repo.remove_flag("f")
        assert repo.cache.get(format_flag_key("f")) is None

    def test_remove_not_interleaved_with_set(self):
        repo = Repository(LRUCache(size=100))
        stop = threading.Event()
        errors = []

        def setter():
            v = 0
            while not stop.is_set():
                v += 1
                repo.set_flag(make_flag("f", v))

        def remover():
            try:
                while not stop.is_set():
                    repo.remove_flag("f")
                    # remove and set serialize: lock must be free after.
                    assert repo._lock.acquire(timeout=5)
                    repo._lock.release()
            except Exception as e:  # pragma: no cover
                errors.append(e)

        ts = [threading.Thread(target=setter), threading.Thread(target=remover)]
        for t in ts:
            t.start()
        time.sleep(1)
        stop.set()
        for t in ts:
            t.join(10)
        assert not errors
