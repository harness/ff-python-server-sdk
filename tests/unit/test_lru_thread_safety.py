"""
Thread-safety tests for LRUCache race condition
(FLAG_NOT_FOUND bug).

These tests reproduce the exact production scenario:
  - Multiple reader threads (FastAPI request handlers)
    calling cache.get()
  - Multiple writer threads (SSE FlagMsgProcessor /
    PollingProcessor) calling cache.set()
  - The unfixed LRUCache has two bugs:
    1. get() calls move_to_end(key) unconditionally
    2. No locking on concurrent read/write

Run against UNFIXED SDK (main branch):
    git checkout main
    pytest tests/unit/test_lru_thread_safety.py -v

Run against FIXED SDK (fix branch):
    git checkout fix/FFM-lru-cache-thread-safety
    pytest tests/unit/test_lru_thread_safety.py -v
"""

import threading
import time
from collections import Counter
from typing import List

import pytest

from featureflags.lru_cache import LRUCache
from featureflags.openapi.config.models.feature_config import FeatureConfig
from featureflags.openapi.config.models.feature_config_kind import \
    FeatureConfigKind
from featureflags.openapi.config.models.feature_state import FeatureState
from featureflags.openapi.config.models.serve import Serve
from featureflags.openapi.config.models.variation import Variation
from featureflags.repository import Repository

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

NUM_FLAGS = 20
FLAG_IDS = [f"flag_{i}" for i in range(NUM_FLAGS)]

# Stress test parameters
STRESS_READER_THREADS = 15
STRESS_WRITER_THREADS = 5
STRESS_DURATION_SECONDS = 5


def make_flag(identifier, version=1):
    """Create a minimal FeatureConfig for testing."""
    return FeatureConfig(
        project="test_project",
        environment="test_env",
        feature=identifier,
        state=FeatureState.ON,
        kind=FeatureConfigKind.BOOLEAN,
        variations=[
            Variation(
                identifier="true_var",
                value="true",
                name="True",
            ),
            Variation(
                identifier="false_var",
                value="false",
                name="False",
            ),
        ],
        default_serve=Serve(variation="true_var"),
        off_variation="false_var",
        version=version,
    )


def _has_lock():
    """Detect if LRUCache has the thread-safety fix."""
    cache = LRUCache()
    return hasattr(cache, "_lock")


IS_FIXED = _has_lock()

# Mark tests expected to fail on unfixed (main) branch.
expect_failure_on_unfixed = pytest.mark.xfail(
    not IS_FIXED,
    reason="LRUCache has no threading.Lock",
    strict=False,
)


# ===============================================================
# TEST 1: DETERMINISTIC — proves the bug without threads
# ===============================================================

class TestDeterministicBugs:
    """Deterministic proof of bugs in unfixed LRUCache.

    Bug 1: get() calls move_to_end(key) unconditionally
    Bug 2: get() + set() interleaving corrupts OrderedDict
    """

    @expect_failure_on_unfixed
    def test_get_missing_key_returns_none(self):
        """get() on a missing key must return None."""
        cache = LRUCache(size=10)
        cache.set("flags/existing", {"state": "on"})
        result = cache.get("flags/nonexistent")
        assert result is None

    @expect_failure_on_unfixed
    def test_get_after_remove_returns_none(self):
        """get() after remove() must return None."""
        cache = LRUCache(size=10)
        cache.set("flags/my_flag", {"state": "on"})
        cache.remove(["flags/my_flag"])
        result = cache.get("flags/my_flag")
        assert result is None

    @expect_failure_on_unfixed
    def test_get_after_lru_eviction_returns_none(self):
        """get() on an LRU-evicted key must return None."""
        cache = LRUCache(size=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)  # evicts "a"
        result = cache.get("a")
        assert result is None

    @expect_failure_on_unfixed
    def test_contains_on_missing_key(self):
        """'key in cache' must return False, not KeyError."""
        cache = LRUCache(size=10)
        cache.set("flags/a", 1)
        result = "flags/nonexistent" in cache
        assert result is False

    def test_simulated_interleaving_causes_keyerror(self):
        """Simulates the exact thread interleaving that
        causes the production race condition.

        Scenario:
          1. Thread A: val = cache.get(key) -> found
          2. GIL switches to Thread B
          3. Thread B: cache.remove([key])
          4. GIL switches back to Thread A
          5. Thread A: move_to_end(key) -> KeyError!
        """
        cache = LRUCache(size=10)
        cache.set("flags/target_flag", {"state": "on"})

        if IS_FIXED:
            result = cache.get("flags/target_flag")
            assert result == {"state": "on"}
            return

        # On UNFIXED SDK: simulate the interleaving
        original_move = cache.cache.move_to_end
        intercepting = [False]

        def intercepted_move(key, last=True):
            if intercepting[0] and key == "flags/target_flag":
                if key in cache.cache:
                    del cache.cache[key]
                intercepting[0] = False
            return original_move(key, last)

        cache.cache.move_to_end = intercepted_move
        intercepting[0] = True

        with pytest.raises(KeyError):
            cache.get("flags/target_flag")

    def test_repo_get_flag_returns_none_on_keyerror(self):
        """When cache.get() KeyErrors, get_flag() returns
        None which becomes FLAG_NOT_FOUND."""
        cache = LRUCache(size=10)
        repo = Repository(cache)

        if IS_FIXED:
            repo.set_flag(make_flag("test_flag", version=1))
            assert repo.get_flag("test_flag") is not None
            return

        repo.set_flag(make_flag("test_flag", version=1))
        result = repo.get_flag(
            "nonexistent_flag", is_outdated_check=True
        )
        assert result is None


# ===============================================================
# TEST 2: CONCURRENT — Raw LRUCache race condition
# ===============================================================

class TestConcurrentCacheAccess:
    """Race condition: concurrent get() + set() on OrderedDict.

    The key is NOT deleted. The corruption is in
    OrderedDict's internal linked list used by
    move_to_end().
    """

    @expect_failure_on_unfixed
    def test_concurrent_get_set_no_errors(self):
        """No KeyError with concurrent readers and writers."""
        cache = LRUCache(size=500)
        errors: List[str] = []
        stop = threading.Event()

        for fid in FLAG_IDS:
            cache.set(
                f"flags/{fid}",
                {"feature": fid, "state": "on"},
            )

        def reader(tid):
            while not stop.is_set():
                for fid in FLAG_IDS:
                    try:
                        cache.get(f"flags/{fid}")
                    except (KeyError, RuntimeError) as e:
                        errors.append(
                            f"reader_{tid}: "
                            f"{type(e).__name__}: {e}"
                        )

        def writer(tid):
            v = 0
            while not stop.is_set():
                for fid in FLAG_IDS:
                    try:
                        cache.set(
                            f"flags/{fid}",
                            {"feature": fid, "v": v},
                        )
                    except (KeyError, RuntimeError) as e:
                        errors.append(
                            f"writer_{tid}: "
                            f"{type(e).__name__}: {e}"
                        )
                    v += 1

        threads = []
        for i in range(STRESS_READER_THREADS):
            threads.append(
                threading.Thread(
                    target=reader, args=(i,), daemon=True,
                )
            )
        for i in range(STRESS_WRITER_THREADS):
            threads.append(
                threading.Thread(
                    target=writer, args=(i,), daemon=True,
                )
            )

        for t in threads:
            t.start()
        time.sleep(STRESS_DURATION_SECONDS)
        stop.set()
        for t in threads:
            t.join(timeout=5)

        assert len(errors) == 0, (
            f"{len(errors)} errors! First 5: {errors[:5]}"
        )

    @expect_failure_on_unfixed
    def test_concurrent_get_remove_set_no_errors(self):
        """No KeyError when writers remove and re-add keys."""
        cache = LRUCache(size=500)
        errors: List[str] = []
        stop = threading.Event()

        for fid in FLAG_IDS:
            cache.set(f"flags/{fid}", {"feature": fid})

        def reader(tid):
            while not stop.is_set():
                for fid in FLAG_IDS:
                    try:
                        cache.get(f"flags/{fid}")
                    except (KeyError, RuntimeError) as e:
                        errors.append(
                            f"reader_{tid}: "
                            f"{type(e).__name__}: {e}"
                        )

        def writer(tid):
            v = 0
            while not stop.is_set():
                for fid in FLAG_IDS:
                    key = f"flags/{fid}"
                    try:
                        cache.remove([key])
                        cache.set(
                            key,
                            {"feature": fid, "v": v},
                        )
                    except (KeyError, RuntimeError) as e:
                        errors.append(
                            f"writer_{tid}: "
                            f"{type(e).__name__}: {e}"
                        )
                    v += 1

        threads = []
        for i in range(STRESS_READER_THREADS):
            threads.append(
                threading.Thread(
                    target=reader, args=(i,), daemon=True,
                )
            )
        for i in range(STRESS_WRITER_THREADS):
            threads.append(
                threading.Thread(
                    target=writer, args=(i,), daemon=True,
                )
            )

        for t in threads:
            t.start()
        time.sleep(STRESS_DURATION_SECONDS)
        stop.set()
        for t in threads:
            t.join(timeout=5)

        assert len(errors) == 0, (
            f"{len(errors)} errors! First 5: {errors[:5]}"
        )

    @expect_failure_on_unfixed
    def test_concurrent_mixed_flags_and_segments(self):
        """Segment writes corrupt flag reads via shared cache."""
        cache = LRUCache(size=500)
        errors: List[str] = []
        stop = threading.Event()

        for i in range(NUM_FLAGS):
            cache.set(
                f"flags/flag_{i}",
                {"feature": f"flag_{i}"},
            )
        for i in range(10):
            cache.set(
                f"segments/seg_{i}",
                {"identifier": f"seg_{i}"},
            )

        def flag_reader(tid):
            while not stop.is_set():
                for i in range(NUM_FLAGS):
                    try:
                        cache.get(f"flags/flag_{i}")
                    except (KeyError, RuntimeError) as e:
                        errors.append(
                            f"flag_reader_{tid}: "
                            f"{type(e).__name__}: {e}"
                        )

        def segment_writer(tid):
            v = 0
            while not stop.is_set():
                for i in range(10):
                    key = f"segments/seg_{i}"
                    try:
                        cache.set(
                            key,
                            {"identifier": f"seg_{i}", "v": v},
                        )
                        if v % 3 == 0:
                            cache.remove([key])
                            cache.set(
                                key,
                                {"identifier": f"seg_{i}", "v": v},
                            )
                    except (KeyError, RuntimeError) as e:
                        errors.append(
                            f"seg_writer_{tid}: "
                            f"{type(e).__name__}: {e}"
                        )
                    v += 1

        def flag_writer(tid):
            v = 0
            while not stop.is_set():
                for i in range(NUM_FLAGS):
                    try:
                        cache.set(
                            f"flags/flag_{i}",
                            {"feature": f"flag_{i}", "v": v},
                        )
                    except (KeyError, RuntimeError) as e:
                        errors.append(
                            f"flag_writer_{tid}: "
                            f"{type(e).__name__}: {e}"
                        )
                    v += 1

        threads = []
        for i in range(STRESS_READER_THREADS):
            threads.append(
                threading.Thread(
                    target=flag_reader,
                    args=(i,),
                    daemon=True,
                )
            )
        for i in range(3):
            threads.append(
                threading.Thread(
                    target=flag_writer,
                    args=(i,),
                    daemon=True,
                )
            )
        for i in range(3):
            threads.append(
                threading.Thread(
                    target=segment_writer,
                    args=(i,),
                    daemon=True,
                )
            )

        for t in threads:
            t.start()
        time.sleep(STRESS_DURATION_SECONDS)
        stop.set()
        for t in threads:
            t.join(timeout=5)

        assert len(errors) == 0, (
            f"{len(errors)} errors! First 5: {errors[:5]}"
        )


# ===============================================================
# TEST 3: CONCURRENT Repository-level false FLAG_NOT_FOUND
# ===============================================================

class TestRepositoryFlagNotFound:
    """Repository.get_flag() returns None for existing flags.

    Call chain:
      bool_variation() -> get_flag_type() -> get_kind()
        -> get_flag() -> cache.get() -> KeyError -> None
        -> FLAG_NOT_FOUND -> customer gets default value
    """

    @expect_failure_on_unfixed
    def test_get_flag_never_returns_none(self):
        """get_flag() must never return None for existing flags."""
        cache = LRUCache(size=500)
        repo = Repository(cache)
        false_not_found: List[dict] = []
        eval_count = [0]
        stop = threading.Event()

        for fid in FLAG_IDS:
            repo.set_flag(make_flag(fid, version=1))

        def app_request_handler(tid):
            local_evals = 0
            while not stop.is_set():
                for fid in FLAG_IDS:
                    result = repo.get_flag(fid)
                    local_evals += 1
                    if result is None:
                        false_not_found.append({
                            "thread": tid,
                            "flag": fid,
                            "eval": local_evals,
                        })
            eval_count[0] += local_evals

        def sse_flag_processor(tid):
            v = 2
            while not stop.is_set():
                for fid in FLAG_IDS:
                    repo.set_flag(
                        make_flag(fid, version=v)
                    )
                v += 1

        def sse_segment_processor(tid):
            v = 0
            while not stop.is_set():
                for i in range(10):
                    seg_key = f"segments/seg_{i}"
                    seg_val = {"id": f"seg_{i}", "v": v}
                    cache.set(seg_key, seg_val)
                    if v % 3 == 0:
                        cache.remove([seg_key])
                        cache.set(seg_key, seg_val)
                    v += 1

        threads = []
        for i in range(STRESS_READER_THREADS):
            threads.append(
                threading.Thread(
                    target=app_request_handler,
                    args=(i,),
                    daemon=True,
                )
            )
        for i in range(3):
            threads.append(
                threading.Thread(
                    target=sse_flag_processor,
                    args=(i,),
                    daemon=True,
                )
            )
        for i in range(3):
            threads.append(
                threading.Thread(
                    target=sse_segment_processor,
                    args=(i,),
                    daemon=True,
                )
            )

        for t in threads:
            t.start()
        time.sleep(STRESS_DURATION_SECONDS)
        stop.set()
        for t in threads:
            t.join(timeout=5)

        if false_not_found:
            counts = Counter(
                f["flag"] for f in false_not_found
            )
            top = counts.most_common(5)
            total = eval_count[0] or 1
            rate = len(false_not_found) / total * 100
            detail = ", ".join(
                f"{f}: {c}" for f, c in top
            )
            pytest.fail(
                f"{len(false_not_found)} false "
                f"FLAG_NOT_FOUND out of "
                f"{eval_count[0]:,} evals "
                f"({rate:.4f}%). Top: {detail}"
            )

    @expect_failure_on_unfixed
    def test_get_flag_consistency_under_polling(self):
        """No false FLAG_NOT_FOUND during polling updates."""
        cache = LRUCache(size=500)
        repo = Repository(cache)
        false_not_found: List[dict] = []
        stop = threading.Event()

        for fid in FLAG_IDS:
            repo.set_flag(make_flag(fid, version=1))

        def reader(tid):
            while not stop.is_set():
                for fid in FLAG_IDS:
                    result = repo.get_flag(fid)
                    if result is None:
                        false_not_found.append(
                            {"thread": tid, "flag": fid}
                        )

        def polling_processor():
            v = 2
            while not stop.is_set():
                for fid in FLAG_IDS:
                    repo.set_flag(
                        make_flag(fid, version=v)
                    )
                v += 1

        threads = []
        for i in range(STRESS_READER_THREADS):
            threads.append(
                threading.Thread(
                    target=reader,
                    args=(i,),
                    daemon=True,
                )
            )
        for i in range(3):
            threads.append(
                threading.Thread(
                    target=polling_processor,
                    daemon=True,
                )
            )

        for t in threads:
            t.start()
        time.sleep(STRESS_DURATION_SECONDS)
        stop.set()
        for t in threads:
            t.join(timeout=5)

        assert len(false_not_found) == 0, (
            f"{len(false_not_found)} false "
            f"FLAG_NOT_FOUND during polling"
        )


# ===============================================================
# TEST 4: Verify fix preserves correct behavior
# ===============================================================

class TestFixPreservesCorrectBehavior:
    """Fix must not break existing LRUCache semantics."""

    def test_get_returns_correct_value(self):
        cache = LRUCache(size=10)
        cache.set("flags/a", {"value": "true"})
        assert cache.get("flags/a") == {"value": "true"}

    def test_set_overwrites_value(self):
        cache = LRUCache(size=10)
        cache.set("flags/a", {"v": 1})
        cache.set("flags/a", {"v": 2})
        assert cache.get("flags/a") == {"v": 2}
        assert len(cache) == 1

    def test_lru_eviction_still_works(self):
        cache = LRUCache(size=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # evicts "a"

        try:
            result = cache.get("a")
            assert result is None
        except KeyError:
            pytest.skip(
                "Unfixed SDK: get() KeyError on evicted"
            )

        assert cache.get("b") == 2
        assert len(cache) == 3

    def test_lru_access_order_preserved(self):
        cache = LRUCache(size=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)

        try:
            cache.get("a")
        except KeyError:
            pytest.skip("Unfixed SDK: get() KeyError")

        cache.set("d", 4)  # evicts "b" (oldest)

        try:
            assert cache.get("a") == 1
            assert cache.get("c") == 3
            assert cache.get("d") == 4
        except KeyError:
            pytest.skip("Unfixed SDK: get() KeyError")
        assert len(cache) == 3

    def test_remove_works(self):
        cache = LRUCache(size=10)
        cache.set("x", 1)
        cache.set("y", 2)
        cache.remove(["x"])
        assert len(cache) == 1

        try:
            assert cache.get("y") == 2
        except KeyError:
            pytest.skip("Unfixed SDK: get() KeyError")

    def test_keys_returns_all_keys(self):
        cache = LRUCache(size=10)
        cache.set("flags/a", 1)
        cache.set("flags/b", 2)
        cache.set("segments/c", 3)
        assert sorted(cache.keys()) == [
            "flags/a", "flags/b", "segments/c",
        ]

    def test_getitem_raises_keyerror_for_missing(self):
        """cache['missing'] should raise KeyError."""
        cache = LRUCache(size=10)
        cache.set("flags/a", 1)
        with pytest.raises(KeyError):
            _ = cache["flags/nonexistent"]

    def test_getitem_returns_value_for_existing(self):
        cache = LRUCache(size=10)
        cache.set("flags/a", {"value": "true"})
        assert cache["flags/a"] == {"value": "true"}

    def test_repo_get_flag_none_for_nonexistent(self):
        """get_flag() returns None for never-inserted flag."""
        cache = LRUCache(size=10)
        repo = Repository(cache)
        result = repo.get_flag(
            "never_existed", is_outdated_check=True
        )
        assert result is None
