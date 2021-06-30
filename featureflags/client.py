"""Client for interacting with Harness FF server"""

from featureflags.evaluations.segment import Segments
from featureflags.lru_cache import LRUCache
import threading
from typing import Any, Callable, Dict, Optional

from jwt import decode

from featureflags.streaming import StreamProcessor
from featureflags.evaluations.feature import FeatureConfig

from .api.client import AuthenticatedClient, Client
from .api.default.authenticate import AuthenticationRequest
from .api.default.authenticate import sync as authenticate
from .api.default.get_feature_config import sync as retrieve_flags
from .api.default.get_all_segments import sync as retrieve_segments
from .streaming import StreamProcessor
from .config import Config, default_config
from .evaluations.target import Target
from .util import log

VERSION: str = "1.0"


class CfClient(object):
    def __init__(
        self, sdk_key: str, *options: Callable, config: Optional[Config] = None
    ):
        self.__client = None
        self.__auth_token = None
        self.__environment_id = None
        self.__sdk_key = sdk_key
        self.__config = default_config

        if config:
            self.__config = config

        for option in options:
            if callable(option):
                option(self.__config)

        log.debug("CfClient initialized")
        self.run()

    def run(self):
        self.authenticate()
        self.cron_segments()
        self.cron_flags()

        event = threading.Event()

        if self.__config.enable_stream:
            self.stream = StreamProcessor(cache=self.__config.cache,
                                          client=self.__client,
                                          environment_id=self.__environment_id,
                                          api_key=self.__sdk_key,
                                          token= self.__auth_token,
                                          config=self.__config,
                                          ready=event)
            self.stream.start()


    def get_environment_id(self):
        return self.__environment_id

    def cron_flags(self):
        self.__retrieve_flags()

    def cron_segments(self):
        self.__retrieve_segments()

    def authenticate(self):
        client = Client(base_url=self.__config.base_url)
        body = AuthenticationRequest(api_key=self.__sdk_key)
        result = authenticate(client=client, json_body=body)
        self.__auth_token = result.auth_token

        decoded = decode(self.__auth_token, options={"verify_signature": False})
        self.__environment_id = decoded["environment"]
        self.__client = AuthenticatedClient(
            base_url=self.__config.base_url, token=self.__auth_token
        )
        self.__client.with_headers({"User-Agent": "PythonSDK/" + VERSION})

    def __retrieve_flags(self):
        flags = retrieve_flags(
            client=self.__client, environment_uuid=self.__environment_id
        )
        for flag in flags:
            log.debug("Setting the cache value %s", flag.feature)
            self.__config.cache.set(f"flags/{flag.feature}", flag)

    def __retrieve_segments(self):
        segments = retrieve_segments(
            client=self.__client, environment_uuid=self.__environment_id
        )
        for segment in segments:
            log.debug("Setting the cache segment value %s", segment.identifier)
            self.__config.cache.set(f"segments/{segment.identifier}", segment)

    def map_segments_from_cache(self, fc: FeatureConfig) -> None:
        if self.__config.cache:
            segments = fc.get_segment_identifiers()
            for identifier in segments:
                segment = self.__config.cache.get(f'segments/{identifier}')
                if fc.segments is None:
                    fc.segments = Segments({})
                fc.segments[identifier] = segment

    def _variation(self, fn: str, identifier: str, target: Target, default: Any) -> Any:
        if self.__config.cache:
            fc = self.__config.cache.get(f'flags/{identifier}')
            if fc:
                self.map_segments_from_cache(fc)
                method = getattr(fc, fn, None)
                if method:
                    variation = method(target)
                    if variation is None:
                        log.debug('No variation found')
                        return default
                    return variation.bool()
                else:
                    log.error("Wrong method name %s", fn)
        return default


    def bool_variation(self, identifier: str, target: Target, default: bool) -> bool:
        return self._variation('bool_variation', identifier, target, default)

    def int_variation(self, identifier: str, target: Target, default: int) -> int:
        return self._variation('int_variation', identifier, target, default)

    def number_variation(self, identifier: str, target: Target, default: float) -> float:
        return self._variation('number_variation', identifier, target, default)

    def string_variation(self, identifier: str, target: Target, default: str) -> str:
        return self._variation('string_variation', identifier, target, default)

    def json_variation(self, identifier: str, target: Target, default: Dict[str, Any]) -> Dict[str, Any]:
        return self._variation('number_variation', identifier, target, default)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
