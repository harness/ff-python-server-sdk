import threading
from collections import OrderedDict
from typing import Any, List

from featureflags.util import log

from .interface import Cache


class LRUCache(Cache):
    def __init__(self, *args: Any, size: int = 2500, **kwargs: Any) -> None:
        self.size = size
        self._lock = threading.Lock()
        init = args
        if len(init) > 0:
            init = args[0][-size:]
        self.cache: OrderedDict = OrderedDict(init)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __getitem__(self, key: str) -> Any:
        with self._lock:
            if key not in self.cache:
                raise KeyError(key)
            val = self.cache[key]
            self.cache.move_to_end(key)
            return val

    def __setitem__(self, key: str, value: Any) -> Any:
        with self._lock:
            self.cache[key] = value
            self.cache.move_to_end(key)

            while len(self.cache) > self.size:
                oldkey = next(iter(self.cache))
                del self.cache[oldkey]
                log.warning("key evicted from cache: %s", oldkey)

    def __len__(self) -> int:
        with self._lock:
            return len(self.cache)

    def set(self, key: str, value: Any) -> None:
        self.__setitem__(key, value)

    def get(self, key: str) -> Any:
        with self._lock:
            val = self.cache.get(key)
            if val is not None:
                self.cache.move_to_end(key)
            return val

    def remove(self, keys: List[str]) -> None:
        with self._lock:
            for key in keys:
                if key in self.cache:
                    del self.cache[key]

    def keys(self) -> List[str]:
        with self._lock:
            return list(self.cache.keys())
