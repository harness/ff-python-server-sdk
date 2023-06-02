"""Client for interacting with Harness FF server"""

import threading
from typing import Any, Callable, Dict, Optional

from tenacity import RetryError
from jwt import decode

from featureflags.analytics import AnalyticsService
from featureflags.evaluations.evaluator import Evaluator
from featureflags.repository import Repository

from .api.client import AuthenticatedClient, Client
from .api.default.authenticate import AuthenticationRequest
from .api.default.authenticate import UnrecoverableAuthenticationException
from .api.default.authenticate import sync as authenticate
from .config import Config, default_config
from .evaluations.auth_target import Target
from .polling import PollingProcessor
from .streaming import StreamProcessor
from .util import log

VERSION: str = "1.0"


class CfClient(object):
    def __init__(
            self, sdk_key: str,
            *options: Callable,
            config: Optional[Config] = None
    ):
        self._client: Optional[Client] = None
        #  The Client is considered initialized when flags and groups
        #  are loaded into cache.
        self._initialized = threading.Event()
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

        if self._config.cache is None:
            raise Exception("cache cannot be none")

        self._repository = Repository(self._config.cache)
        self._evaluator = Evaluator(self._repository)

        self.run()

    def run(self):
        try:
            self.authenticate()
            streaming_event = threading.Event()
            polling_event = threading.Event()

            self._polling_processor = PollingProcessor(
                client=self._client,
                config=self._config,
                environment_id=self._environment_id,
                #  PollingProcessor is responsible for doing the initial
                #  flag/group fetch and cache. So we allocate it the
                #  responsibility
                #  for setting the Client is_initialized variable.
                wait_for_initialization=self._initialized,
                ready=polling_event,
                stream_ready=streaming_event,
                repository=self._repository
            )
            self._polling_processor.start()

            if self._config.enable_stream:
                self._stream = StreamProcessor(
                    repository=self._repository,
                    client=self._client,
                    environment_id=self._environment_id,
                    api_key=self._sdk_key,
                    token=self._auth_token,
                    config=self._config,
                    ready=streaming_event,
                    poller=polling_event,
                    cluster=self._cluster,
                )
                self._stream.start()

            if self._config.enable_analytics:
                self._analytics = AnalyticsService(
                    config=self._config,
                    client=self._client,
                    environment=self._environment_id
                )

        except RetryError:
            log.error(
                "Authentication failed and max retries have been exceeded - "
                "defaults will be served.")
            # Mark the client as initialized in case wait_for_initialization
            # is called. The SDK has already logged that authentication
            # failed and defaults will be returned.
            self._initialized.set()
        except UnrecoverableAuthenticationException:
            log.error(
                "Authentication failed - defaults will be served.")
            # Same again, just mark the client as initailized.
            self._initialized.set()

    def wait_for_initialization(self):
        log.debug("Waiting for initialization to finish")
        self._initialized.wait()

    def is_initialized(self):
        return self._initialized.is_set()

    def get_environment_id(self):
        return self._environment_id

    def authenticate(self):
        client = Client(
            base_url=self._config.base_url,
            events_url=self._config.events_url,
            max_auth_retries=self._config.max_auth_retries
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
            },
            max_auth_retries=self._config.max_auth_retries
        )
        # Additional headers used to track usage
        additional_headers = {
            "User-Agent": "PythonSDK/" + VERSION,
            "Harness-SDK-Info": f'Python {VERSION} Server',
            "Harness-EnvironmentID": self._environment_id,
            "Harness-AccountID": decoded["accountID"]}
        self._client = self._client.with_headers(additional_headers)

    def bool_variation(self, identifier: str, target: Target,
                       default: bool) -> bool:
        variation = self._evaluator.evaluate(identifier, target)
        # Only register metrics if analytics is enabled,
        # and sometimes when the SDK starts up we can
        # evaluate before the flag is cached which results in
        # an empty identifier.
        if self._config.enable_analytics and variation.identifier != "":
            self._analytics.enqueue(target, identifier, variation)
        return variation.bool(target, identifier, default)

    def int_variation(self, identifier: str, target: Target,
                      default: int) -> int:
        variation = self._evaluator.evaluate(identifier, target)
        # Only register metrics if analytics is enabled,
        # and sometimes when the SDK starts up we can
        # evaluate before the flag is cached which results in
        # an empty identifier.
        if self._config.enable_analytics and variation.identifier != "":
            self._analytics.enqueue(target, identifier, variation)
        return variation.int(target, identifier, default)

    def number_variation(self, identifier: str, target: Target,
                         default: float) -> float:
        variation = self._evaluator.evaluate(
            identifier, target)
        # Only register metrics if analytics is enabled,
        # and sometimes when the SDK starts up we can
        # evaluate before the flag is cached which results in
        # an empty identifier.
        if self._config.enable_analytics and variation.identifier != "":
            self._analytics.enqueue(target, identifier, variation)
        return variation.number(target, identifier, default)

    def string_variation(self, identifier: str, target: Target,
                         default: str) -> str:
        variation = self._evaluator.evaluate(
            identifier, target)
        # Only register metrics if analytics is enabled,
        # and sometimes when the SDK starts up we can
        # evaluate before the flag is cached which results in
        # an empty identifier.
        if self._config.enable_analytics and variation.identifier != "":
            self._analytics.enqueue(target, identifier, variation)
        return variation.string(target, identifier, default)

    def json_variation(self, identifier: str, target: Target,
                       default: Dict[str, Any]) -> Dict[str, Any]:
        variation = self._evaluator.evaluate(identifier, target)
        # Only register metrics if analytics is enabled,
        # and sometimes when the SDK starts up we can
        # evaluate before the flag is cached which results in
        # an empty identifier.
        if self._config.enable_analytics and variation.identifier != "":
            self._analytics.enqueue(target, identifier, variation)
        return variation.json(target, identifier, default)

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
