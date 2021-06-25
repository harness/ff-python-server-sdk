"""Client for interacting with Harness FF server"""

from typing import Any, Callable, Optional

from jwt import decode

from .api.client import AuthenticatedClient, Client
from .api.default.authenticate import AuthenticationRequest
from .api.default.authenticate import sync as authenticate
from .api.default.get_feature_config import sync as retrieve_flags
from .api.default.get_all_segments import sync as retrieve_segments
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
        self.concurrent()

    def concurrent(self):
        self.authenticate()
        self.cron_flags()
        self.cron_segments()

    def get_environment_id(self):
        return self.__environment_id

    def cron_flags(self):
        self.retrieve_flags()

    def cron_segments(self):
        self.retrieve_segments()

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

    def retrieve_flags(self):
        flags = retrieve_flags(
            client=self.__client, environment_uuid=self.__environment_id
        )
        for flag in flags:
            log.debug("Setting the cache value %s", flag.feature)
            self.__config.cache.set(f"flags/{flag.feature}", flag)

    def retrieve_segments(self):
        segments = retrieve_segments(
            client=self.__client, environment_uuid=self.__environment_id
        )
        for segment in segments:
            log.debug("Setting the cache segment value %s", segment.identifier)
            self.__config.cache.set(f"segments/{segment.identifier}", segment)

    def bool_variation(self, identifier: str, target: Target, default: bool) -> bool:
        if self.__config.cache:
            fc = self.__config.cache.get(f'flags/{identifier}')
            variation = fc.bool_variation(target)
            if variation is None:
                log.debug('No variation found')
                return default
            return variation.bool()
        return default

    def int_variation(self):
        pass

    def number_variation(self):
        pass

    def string_variation(self):
        pass

    def json_variation(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
