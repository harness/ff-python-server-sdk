"""Client for interacting with Harness FF server"""

import asyncio
from typing import Callable, Optional

from jwt import decode

from .config import Config, default_config
from .rest.client import Client, AuthenticatedClient
from .rest.api.default.authenticate import asyncio as authenticate, \
    AuthenticationRequest
from .rest.api.default.get_feature_config import asyncio as retrieve_flags


class CfClient(object):

    def __init__(self, sdk_key: str, *options: Callable,
                 config: Optional[Config] = None):
        self.__lock = asyncio.Lock()
        self.__client = None
        self.__auth_token = None
        self.__environment_id = None
        self.__sdk_key = sdk_key
        self.__config = default_config
        self.__event = asyncio.Event()

        for option in options:
            if callable(option):
                option(self.__config)

        if config:
            self.__config = config

        asyncio.run(self.concurrent())

    async def concurrent(self):
        auth_task = asyncio.ensure_future(self.authenticate())
        flags_task = asyncio.ensure_future(self.cron_flags())
        await asyncio.gather(auth_task, flags_task)

    def get_environment_id(self):
        with self.__lock:
            return self.__environment_id

    async def cron_flags(self):
        while True:
            await self.retrieve_flags()
            await asyncio.sleep(self.__config.pull_interval)

    async def authenticate(self):
        async with self.__lock:
            client = Client(base_url=self.__config.base_url)
            body = AuthenticationRequest(api_key=self.__sdk_key)
            result = await authenticate(client=client, json_body=body)
            self.__auth_token = result.auth_token

            decoded = decode(self.__auth_token, options={"verify_signature": False})
            self.__environment_id = decoded["environment"]
            self.__client = AuthenticatedClient(base_url=self.__config.base_url,
                                                token=self.__auth_token)
            self.__event.set()

    async def retrieve_flags(self):
        if not self.__event.is_set():
            return
        result = await retrieve_flags(client=self.__client, environment_uuid=self.__environment_id)
        print(result)

    def retrieve_segments(self):
        pass

    def bool_variation(self):
        pass

    def int_variation(self):
        pass

    def number_variation(self):
        pass

    def string_variation(self):
        pass

    def json_variation(self):
        pass
