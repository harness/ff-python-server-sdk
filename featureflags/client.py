"""Client for interacting with Harness FF server"""

import threading
from typing import Any, Callable, Dict, Optional

from jwt import decode

from featureflags.analytics import AnalyticsService

from .api.client import AuthenticatedClient, Client
from .api.default.authenticate import AuthenticationRequest
from .api.default.authenticate import sync as authenticate
from .config import Config, default_config
from .evaluations.feature import FeatureConfig
from .evaluations.segment import Segments
from .evaluations.target import Target
from .polling import PollingProcessor
from .streaming import StreamProcessor
from .util import log

VERSION: str = "1.0"


class CfClient(object):
    def __init__(
        self, sdk_key: str, *options: Callable, config: Optional[Config] = None
    ):
        self._client: Optional[Client] = None
        self._auth_token: Optional[str] = None
        self._environment_id: Optional[str] = None
        self._sdk_key: Optional[str] = sdk_key
        self._config: Config = default_config
        self._cluster: str = '1'

        if config:
            self._config = config

        for option in options:
            if callable(option):
                option(self._config)

        log.debug("CfClient initialized")
        self.run()

    def run(self):
        self.authenticate()

        streaming_event = threading.Event()
        polling_event = threading.Event()

        self._polling_processor = PollingProcessor(
            client=self._client,
            config=self._config,
            environment_id=self._environment_id,
            ready=polling_event,
            stream_ready=streaming_event
        )
        self._polling_processor.start()

        if self._config.enable_stream:
            self._stream = StreamProcessor(
                cache=self._config.cache,
                client=self._client,
                environment_id=self._environment_id,
                api_key=self._sdk_key,
                token=self._auth_token,
                config=self._config,
                ready=streaming_event,
                cluster=self._cluster
            )
            self._stream.start()

        if self._config.enable_analytics:
            self._analytics = AnalyticsService(
                config=self._config,
                client=self._client,
                environment=self._environment_id
            )

    def get_environment_id(self):
        return self._environment_id

    def authenticate(self):
        client = Client(
            base_url=self._config.base_url,
            events_url=self._config.events_url
        )
        body = AuthenticationRequest(api_key=self._sdk_key)
        response = authenticate(client=client, json_body=body)
        self._auth_token = response.auth_token

        decoded = decode(self._auth_token, options={
                         "verify_signature": False})
        self._environment_id = decoded["environment"]
        self._cluster = decoded["clusterIdentifier"]
        if not self._cluster:
            self._cluster = '1'
        self._client = AuthenticatedClient(
            base_url=self._config.base_url,
            events_url=self._config.events_url,
            token=self._auth_token,
            params={
                'cluster': self._cluster
            }
        )
        self._client.with_headers({"User-Agent": "PythonSDK/" + VERSION})

    def map_segments_from_cache(self, fc: FeatureConfig) -> None:
        if self._config.cache:
            segments = fc.get_segment_identifiers()
            for identifier in segments:
                segment = self._config.cache.get(f'segments/{identifier}')
                if fc.segments is None:
                    fc.segments = Segments({})
                fc.segments[identifier] = segment

    def _variation(self, fn: str, identifier: str, target: Target,
                   default: Any) -> Any:
        if self._config.cache:
            fc = self._config.cache.get(f'flags/{identifier}')
            if fc:
                self.map_segments_from_cache(fc)
                method = getattr(fc, fn, None)
                if method:
                    variation = method(target)
                    if variation is None:
                        log.debug('No variation found')
                        return default
                    self._analytics.enqueue(target, fc, variation)
                    return variation.bool()
                else:
                    log.error("Wrong method name %s", fn)
        return default

    def bool_variation(self, identifier: str, target: Target,
                       default: bool) -> bool:
        return self._variation('bool_variation', identifier, target, default)

    def int_variation(self, identifier: str, target: Target,
                      default: int) -> int:
        return self._variation('int_variation', identifier, target, default)

    def number_variation(self, identifier: str, target: Target,
                         default: float) -> float:
        return self._variation('number_variation', identifier, target, default)

    def string_variation(self, identifier: str, target: Target,
                         default: str) -> str:
        return self._variation('string_variation', identifier, target, default)

    def json_variation(self, identifier: str, target: Target,
                       default: Dict[str, Any]) -> Dict[str, Any]:
        return self._variation('number_variation', identifier, target, default)

    def close(self):
        log.info('closing sdk client')
        self._polling_processor.stop()
        if self._config.enable_stream:
            self._stream.stop()

        if self._config.enable_analytics:
            self._analytics.close()
        log.info('All threads finished')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
