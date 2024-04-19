"""Client for interacting with Harness FF server"""

import threading
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union

from tenacity import RetryError
from jwt import decode

from featureflags.analytics import AnalyticsService
from featureflags.evaluations.evaluator import Evaluator, \
    FlagKindMismatchException
from featureflags.repository import Repository

from .openapi.config.client import AuthenticatedClient, Client
from .openapi.config.api.client.authenticate import AuthenticationRequest
# from .openapi.client.api.client.authenticate import UnrecoverableAuthenticationException
from .openapi.config.api.client.authenticate import sync as authenticate
from .config import Config, default_config
from .evaluations.auth_target import Target
from .polling import PollingProcessor
from .streaming import StreamProcessor
import featureflags.sdk_logging_codes as sdk_codes
from .util import log
from tenacity import retry_if_result, wait_exponential, \
    stop_after_attempt, Retrying, retry_all
from featureflags.sdk_logging_codes import warn_auth_retying
from featureflags.config import RETRYABLE_CODES
import json

VERSION: str = "1.7.0"


class MissingOrEmptyAPIKeyException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"MissingOrEmptyAPIKeyException: {self.message}"


class FeatureFlagType(str, Enum):
    BOOLEAN = "boolean"
    INT_OR_FLOAT = "int"
    STRING = "string"
    JSON = "json"
    FLAG_NOT_FOUND = "flag_not_found"


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
        # Keep track if initialization has failed due to authentication
        # or a missing/empty API key.
        self._initialized_failed = False
        self._initialised_failed_reason: Dict[bool, Optional[str]] \
            = {False: None, True: None}
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
            if self._sdk_key is None:
                raise MissingOrEmptyAPIKeyException("SDK Key is None")

            if self._sdk_key == "":
                raise MissingOrEmptyAPIKeyException("SDK Key is an empty "
                                                    "string")

            self.authenticate()
            sdk_codes.info_sdk_auth_ok()
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
                initialised_failed_reason=self._initialised_failed_reason,
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
            sdk_codes.warn_auth_failed_exceed_retries()
            sdk_codes.warn_failed_init_auth_error()
            self._initialized_failed = True
            # We just need to unblock the thread here
            # in case wait_for_intialization was called. The SDK has already
            # logged that authentication failed and defaults will be returned.
            self._initialized.set()
        # except UnrecoverableAuthenticationException as ex:
        #     self._initialized_failed = True
        #     self._initialised_failed_reason[True] \
        #         = str(ex)
        #     sdk_codes.warn_auth_failed_srv_defaults()
        #     sdk_codes.warn_failed_init_auth_error()
        #     # Same again, unblock the thread.
        #     self._initialized.set()
        except MissingOrEmptyAPIKeyException:
            self._initialized_failed = True
            self._initialised_failed_reason[True] \
                = str(MissingOrEmptyAPIKeyException)
            sdk_codes.wan_missing_sdk_key()
            # And again, unblock the thread.
            self._initialized.set()
        except Exception as ex:
            sdk_codes.warn_failed_init_auth_error(str(ex))
            self._initialised_failed_reason[True] \
                = str(ex)
            self._initialized.set()

    def wait_for_initialization(self):
        sdk_codes.info_sdk_init_waiting()
        self._initialized.wait()

    def is_initialized(self):
        if self._initialized_failed \
                or self._initialised_failed_reason[True] is not None:
            return False
        return self._initialized.is_set()

    def get_environment_id(self):
        return self._environment_id

    def _handle_http_result(response):
        code = response.status_code
        if code in RETRYABLE_CODES:
            return True
        else:
            log.error(
                f'Authentication received HTTP code #{code} and '
                'will not attempt to reconnect')
            return False

    def _authenticate_with_retry(self, client, body, max_auth_retries):
        retryer = Retrying(
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_all(
                retry_if_result(lambda response: response.status_code != 200),
                retry_if_result(self._handle_http_result)
            ),
            before_sleep=lambda retry_state: warn_auth_retying(
                retry_state.attempt_number,
                retry_state.outcome.result()),
            stop=stop_after_attempt(max_auth_retries),
        )
        return retryer(authenticate, client=client, body=body)

    def authenticate(self):
        verify = True
        if self._config.tls_trusted_cas_file is not None:
            verify = self._config.tls_trusted_cas_file

        client = Client(base_url=self._config.base_url, verify_ssl=verify)
        body = AuthenticationRequest(api_key=self._sdk_key)
        response = self._authenticate_with_retry(client=client, body=body,
                                                 max_auth_retries=self._config.max_auth_retries)
        self._auth_token = response.auth_token

        decoded = decode(self._auth_token, options={
            "verify_signature": False})
        self._environment_id = decoded["environment"]
        self._cluster = decoded["clusterIdentifier"]
        if not self._cluster:
            self._cluster = '1'
        self._client = AuthenticatedClient(
            base_url=self._config.base_url,
            token=self._auth_token,
            params={
                'cluster': self._cluster
            }
        )
        # Additional headers used to track usage
        additional_headers = {
            "User-Agent": "PythonSDK/" + VERSION,
            "Harness-SDK-Info": f'Python {VERSION} Server',
            "Harness-EnvironmentID": self._environment_id}
        # At present the FF Relay Proxy does not send the accountID claim
        if "accountID" in decoded:
            additional_headers["Harness-AccountID"] = decoded["accountID"]
        self._client = self._client.with_headers(additional_headers)

    def get_flag_type(self, identifier) -> Optional[FeatureFlagType]:
        if self._initialised_failed_reason[True] is not None:
            log.warning(
                "Failed to check flag type for flag '%s', reason: Client is "
                "not initialized",
                identifier)
            return FeatureFlagType("flag_not_found")
        kind = self._evaluator.get_kind(identifier)
        if not kind:
            log.warning(
                "Failed to check flag kind for flag '%s', reason: flag not "
                "found", identifier)
            return FeatureFlagType("flag_not_found")
        return FeatureFlagType(kind)

    def bool_variation(self, identifier: str, target: Target,
                       default: bool) -> bool:
        # If initialization has failed, then return the default variation
        # immediately
        if self._initialised_failed_reason[True] is not None:
            log.error(
                "SDKCODE:6001: Failed to evaluate bool variation for flag '%s'"
                " and the default variation '%s' is being returned. Reason: "
                "`Client is not initialized: %s'",
                identifier, default, self._initialised_failed_reason[True])
            return default

        try:
            variation = self._evaluator.evaluate(identifier, target, "boolean")

            if not variation or not variation.value:
                log.error(
                    "SDKCODE:6001: Failed to evaluate bool variation for %s and the "
                    "default variation '%s' is being returned",
                    {"target": target, "flag": identifier}, default)
                return default

            # Only register metrics if analytics is enabled,
            # and sometimes when the SDK starts up we can
            # evaluate before the flag is cached which results in
            # an empty identifier.
            if self._config.enable_analytics and variation.identifier != "":
                self._analytics.enqueue(target, identifier, variation)
            return variation.value.lower() == "true"

        except FlagKindMismatchException as ex:
            log.error(
                "SDKCODE:6001: Failed to evaluate bool variation for flag '%s'"
                " and the default variation '%s' is being returned. Reason: "
                "'%s'", identifier, default, str(ex))
            return default

    def int_variation(self, identifier: str, target: Target,
                      default: int) -> int:

        # If initialization has failed, then return the default variation
        # immediately
        if self._initialised_failed_reason[True] is not None:
            log.error(
                "SDKCODE:6001: Failed to evaluate bool variation for flag '%s'"
                " and the default variation '%s' is being returned. Reason: "
                "`Client is not initialized: %s'",
                identifier, default, self._initialised_failed_reason[True])
            return default

        try:
            variation = self._evaluator.evaluate(identifier, target, "int")

            if not variation or not variation.value:
                log.error(
                    "SDKCODE:6001: Failed to evaluate bool variation for %s and the "
                    "default variation '%s' is being returned",
                    {"target": target, "flag": identifier}, default)
                return default

            # Only register metrics if analytics is enabled,
            # and sometimes when the SDK starts up we can
            # evaluate before the flag is cached which results in
            # an empty identifier.
            if self._config.enable_analytics and variation.identifier != "":
                self._analytics.enqueue(target, identifier, variation)

            return int(variation.value)

        except FlagKindMismatchException as ex:
            log.error(
                "SDKCODE:6001: Failed to evaluate int variation for flag '%s'"
                " and the default variation '%s' is being returned. Reason: "
                "'%s'", identifier, default, str(ex))
            return default

    def number_variation(self, identifier: str, target: Target,
                         default: float) -> float:

        # If initialization has failed, then return the default variation
        # immediately
        if self._initialised_failed_reason[True] is not None:
            log.error(
                "SDKCODE:6001: Failed to evaluate number variation for flag "
                "'%s' and the default variation '%s' is being returned. "
                "Reason: `Client is not initialized: %s'",
                identifier, default, self._initialised_failed_reason[True])
            return default

        try:
            variation = self._evaluator.evaluate(
                identifier, target, "int")

            if not variation or not variation.value:
                log.error(
                    "SDKCODE:6001: Failed to evaluate bool variation for %s and the "
                    "default variation '%s' is being returned",
                    {"target": target, "flag": identifier}, default)
                return default

            # Only register metrics if analytics is enabled,
            # and sometimes when the SDK starts up we can
            # evaluate before the flag is cached which results in
            # an empty identifier.
            if self._config.enable_analytics and variation.identifier != "":
                self._analytics.enqueue(target, identifier, variation)

            return float(variation.value)

        except FlagKindMismatchException as ex:
            log.error(
                "SDKCODE:6001: Failed to evaluate number variation for flag "
                "'%s'  and the default variation '%s' is being returned. "
                "Reason: '%s'", identifier, default, str(ex))
            return default

    def int_or_float_variation(self, identifier: str, target: Target,
                               default: Union[float, int]) -> \
            Union[float, int]:

        # If initialization has failed, then return the default variation
        # immediately
        if self._initialised_failed_reason[True] is not None:
            log.error(
                "SDKCODE:6001: Failed to evaluate int_or_float variation for "
                "flag '%s' and the default variation '%s' is being returned. "
                "Reason: `Client is not initialized: %s'",
                identifier, default, self._initialised_failed_reason[True])
            return default

        try:
            variation = self._evaluator.evaluate(
                identifier, target, "int")

            if not variation or not variation.value:
                log.error(
                    "SDKCODE:6001: Failed to evaluate bool variation for %s and the "
                    "default variation '%s' is being returned",
                    {"target": target, "flag": identifier}, default)
                return default

            # Only register metrics if analytics is enabled,
            # and sometimes when the SDK starts up we can
            # evaluate before the flag is cached which results in
            # an empty identifier.
            if self._config.enable_analytics and variation.identifier != "":
                self._analytics.enqueue(target, identifier, variation)

            try:
                result = int(variation.value)
            except ValueError:
                try:
                    result = float(variation.value)
                except ValueError:
                    # If both conversions fail, log an error and return the
                    # default
                    log.error(
                        "SDKCODE:6001: Invalid number format for %s. "
                        "Expected a number but got '%s'",
                        {"flag": identifier, "value": variation.value}
                    )
                    return default

            return result

        except FlagKindMismatchException as ex:
            log.error(
                "SDKCODE:6001: Failed to evaluate int_or_float variation for "
                "flag '%s'  and the default variation '%s' is being returned. "
                "Reason: '%s'", identifier, default, str(ex))
            return default

    def string_variation(self, identifier: str, target: Target,
                         default: str) -> str:

        # If initialization has failed, then return the default variation
        # immediately
        if self._initialised_failed_reason[True] is not None:
            log.error(
                "SDKCODE:6001: Failed to evaluate string variation for flag "
                "'%s' and the default variation '%s' is being returned. "
                "Reason: `Client is not initialized: %s'",
                identifier, default, self._initialised_failed_reason[True])
            return default

        try:
            variation = self._evaluator.evaluate(
                identifier, target, "string")

            if not variation or not variation.value:
                log.error(
                    "SDKCODE:6001: Failed to evaluate bool variation for %s and the "
                    "default variation '%s' is being returned",
                    {"target": target, "flag": identifier}, default)
                return default

            # Only register metrics if analytics is enabled,
            # and sometimes when the SDK starts up we can
            # evaluate before the flag is cached which results in
            # an empty identifier.
            if self._config.enable_analytics and variation.identifier != "":
                self._analytics.enqueue(target, identifier, variation)

            return variation.value

        except FlagKindMismatchException as ex:
            log.error(
                "SDKCODE:6001: Failed to evaluate string variation for flag "
                "'%s' and the default variation '%s' is being returned. "
                "Reason: '%s'", identifier, default, str(ex))
            return default

    def json_variation(self, identifier: str, target: Target,
                       default: Dict[str, Any]) -> Dict[str, Any]:

        # If initialization has failed, then return the default variation
        # immediately
        if self._initialised_failed_reason[True] is not None:
            log.error(
                "SDKCODE:6001: Failed to evaluate json variation for flag '%s'"
                " and the default variation '%s' is being returned. Reason: "
                "`Client is not initialized: %s'",
                identifier, default, self._initialised_failed_reason[True])
            return default

        try:
            variation = self._evaluator.evaluate(identifier, target, "json")

            if not variation or not variation.value:
                log.error(
                    "SDKCODE:6001: Failed to evaluate bool variation for %s and the "
                    "default variation '%s' is being returned",
                    {"target": target, "flag": identifier}, default)
                return default

            # Only register metrics if analytics is enabled,
            # and sometimes when the SDK starts up we can
            # evaluate before the flag is cached which results in
            # an empty identifier.
            if self._config.enable_analytics and variation.identifier != "":
                self._analytics.enqueue(target, identifier, variation)

            return json.loads(variation.value)

        except FlagKindMismatchException as ex:
            log.error(
                "SDKCODE:6001: Failed to evaluate json variation for flag "
                "'%s' and the default variation '%s' is being returned. "
                "Reason: '%s'", identifier, default, str(ex))
            return default

    def close(self):
        sdk_codes.info_sdk_start_close()
        self._polling_processor.stop()
        if self._config.enable_stream:
            self._stream.stop()

        if self._config.enable_analytics:
            self._analytics.close()
        sdk_codes.info_sdk_close_success()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
