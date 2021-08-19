from collections import OrderedDict
from typing import Any, List

from .interface import Cache


class LRUCache(Cache):
    def __init__(self, *args: Any, size: int = 1000, **kwargs: Any) -> None:
        self.size = size
        init = args
        if len(init) > 0:
            init = args[0][-size:]
        self.cache: OrderedDict = OrderedDict(init)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> Any:
        self.cache[key] = value
        self.cache.move_to_end(key)

        while len(self.cache) > self.size:
            oldkey = next(iter(self.cache))
            del self.cache[oldkey]

    def __len__(self) -> int:
        return len(self.cache)

    def set(self, key: str, value: Any) -> None:
        self.__setitem__(key, value)

    def get(self, key: str) -> Any:
        val = self.cache.get(key)
        self.cache.move_to_end(key)
        return val

    def remove(self, keys: List[str]) -> None:
        for key in keys:
            del self.cache[key]

    def keys(self) -> List[str]:
        return list(self.cache.keys())
