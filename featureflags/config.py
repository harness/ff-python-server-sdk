"""Configuration is a base class that has default values that you can change
during the instance of the client class"""

from typing import Callable

BASE_URL = "https://config.feature-flags.uat.harness.io/api/1.0"
MINUTE = 60
PULL_INTERVAL = 1 * MINUTE


class Config(object):

    def __init__(self, base_url: str = BASE_URL,
                 pull_interval: int = PULL_INTERVAL,
                 cache: object = None,
                 store: object = None,
                 enable_stream: bool = False):
        self.base_url = base_url
        self.pull_interval = pull_interval
        self.cache = cache
        self.store = store
        self.enable_stream = enable_stream


default_config = Config()


def with_base_url(base_url: str) -> Callable:
    def func(config: Config) -> None:
        config.base_url = base_url
    return func


def with_stream_enabled(value: bool) -> Callable:
    def func(config: Config) -> None:
        config.enable_stream = value
    return func
