from typing import Any, List
from datetime import datetime, timedelta
from collections import OrderedDict

from .interface import Interface


class LRUCache(Interface):

    def __init__(self, *args, size: int = 1000) -> None:
        self.size = size
        self.cache: OrderedDict = OrderedDict(*args)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> Any:
        self.set(key, value)

    def __len__(self) -> int:
        return len(self.cache)

    def set(self, key: str, value: Any) -> None:
        self.cache[key] = value
        self.cache.move_to_end(key)

        while len(self.cache) > self.size:
            oldkey = next(iter(self.cache))
            del self.cache[oldkey]

    def get(self, key: str) -> Any:
        val = self.cache.get(key)
        self.cache.move_to_end(key)
        return val

    def remove(self, keys: List[str]) -> None:
        for key in keys:
            del self.cache[key]

    def keys(self) -> List[str]:
        return list(self.cache.keys())
