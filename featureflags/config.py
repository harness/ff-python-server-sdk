"""Configuration is a base class that has default values that you can change
during the instance of the client class"""

from typing import Callable

from .interface import Cache
from .lru_cache import LRUCache

BASE_URL = "https://config.ff.harness.io/api/1.0"
EVENTS_URL = "https://events.ff.harness.io/api/1.0"
MINUTE = 60
PULL_INTERVAL = 1 * MINUTE
PERSIST_INTERVAL = 1 * MINUTE
EVENTS_SYNC_INTERVAL = 1 * MINUTE


class Config(object):
    def __init__(
        self,
        base_url: str = BASE_URL,
        events_url: str = EVENTS_URL,
        pull_interval: int = PULL_INTERVAL,
        persist_interval: int = PERSIST_INTERVAL,
        events_sync_interval: int = EVENTS_SYNC_INTERVAL,
        cache: Cache = None,
        store: object = None,
        enable_stream: bool = True,
        enable_analytics: bool = True
    ):
        self.base_url = base_url
        self.events_url = events_url
        self.pull_interval = pull_interval
        self.persist_interval = persist_interval
        self.events_sync_interval = events_sync_interval
        self.cache = cache
        if self.cache is None:
            self.cache = LRUCache()
        self.store = store
        self.enable_stream = enable_stream
        self.enable_analytics = enable_analytics


default_config = Config()


def with_base_url(base_url: str) -> Callable:
    def func(config: Config) -> None:
        config.base_url = base_url

    return func


def with_events_url(events_url: str) -> Callable:
    def func(config: Config) -> None:
        config.events_url = events_url

    return func


def with_stream_enabled(value: bool) -> Callable:
    def func(config: Config) -> None:
        config.enable_stream = value

    return func


def with_analytics_enabled(value: bool) -> Callable:
    def func(config: Config) -> None:
        config.enable_analytics = value

    return func
