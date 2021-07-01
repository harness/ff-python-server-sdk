from collections import namedtuple

import pytest

from featureflags.lru_cache import LRUCache


def test_cache_null():
    """Null dict is null."""
    cache = LRUCache()
    assert cache.__len__() == 0


Case = namedtuple("Case", ["size", "len", "init"])


@pytest.mark.parametrize(
    "case",
    [
        Case(9, 0, []),
        Case(9, 1, [("one", 1)]),
        Case(9, 2, [("one", 1), ("two", 2)]),
        Case(2, 2, [("one", 1), ("two", 2)]),
        Case(1, 1, [("one", 1), ("two", 2)]),
    ],
)
@pytest.mark.parametrize("method", ["assign", "init"])
def test_cache_init(case, method):
    """Check that the # of elements is right, given # given and size."""
    if method == "init":
        cache = LRUCache(case.init, size=case.size)
    elif method == "assign":
        cache = LRUCache(size=case.size)
        for (key, val) in case.init:
            cache[key] = val
    else:
        assert False

    # length is max(#entries, size)
    assert cache.__len__() == case.len

    # make sure the first entry is the one ejected
    if case.size > 1 and case.init:
        assert "one" in cache.keys()
    else:
        assert "one" not in cache.keys()


@pytest.mark.parametrize("method", ["init", "assign"])
def test_cache_overflow_default(method):
    """Test default overflow logic."""
    if method == "init":
        cache = LRUCache([("one", 1), ("two", 2), ("three", 3)], size=2)
    elif method == "assign":
        cache = LRUCache(size=2)
        cache["one"] = 1
        cache["two"] = 2
        cache["three"] = 3
    else:
        assert False

    assert "one" not in cache.keys()
    assert "two" in cache.keys()
    assert "three" in cache.keys()


@pytest.mark.parametrize("mode", ["get", "set"])
@pytest.mark.parametrize("add_third", [True, False])
def test_cache_lru_overflow(mode, add_third):
    """Test that key access resets LRU logic."""

    cache = LRUCache([("one", 1), ("two", 2)], size=2)

    if mode == "get":
        _ = cache["one"]
    elif mode == "set":
        cache["one"] = 1
    else:
        assert False

    if add_third:
        cache["three"] = 3

        assert "one" in cache.keys()
        assert "two" not in cache.keys()
        assert "three" in cache.keys()
    else:
        assert "one" in cache.keys()
        assert "two" in cache.keys()
        assert "three" not in cache.keys()


def test_cache_keyerror():
    cache = LRUCache()
    with pytest.raises(KeyError):
        cache["foo"]


def test_cache_miss_doesnt_eject():
    cache = LRUCache([("one", 1), ("two", 2)], size=2)
    with pytest.raises(KeyError):
        cache["foo"]

    assert len(cache) == 2
    assert "one" in cache.keys()
    assert "two" in cache.keys()
