
import threading
from threading import Thread
from typing import List, Union

from .api.client import AuthenticatedClient
from .api.default.get_feature_config_by_identifier import \
    sync as get_feature_config
from .api.default.get_segment_by_identifier import sync as get_target_segment
from .config import Config
from .interface import Cache
from .models.message import Message
from .sse_client import SSEClient
from .util import log


class StreamProcessor(Thread):
    def __init__(self, cache: Cache, client: AuthenticatedClient,
                 environment_id: str, api_key: str, token: str,
                 config: Config, ready: threading.Event,
                 cluster: str):

        Thread.__init__(self)
        self.daemon = True
        self._running = False
        self._cache = cache
        self._ready = ready
        self._client = client
        self._environment_id = environment_id
        self._api_key = api_key
        self._token = token
        self._stream_url = f'{config.base_url}/stream?cluster={cluster}'
        self._msg_processors: List[Union[FlagMsgProcessor,
                                         SegmentMsgProcessor]] = []

    def run(self):
        log.info("Starting StreamingProcessor connecting to uri: " +
                 self._stream_url)
        self._running = True

        while self._running:
            try:
                messages = self._connect()
                for msg in messages:
                    if not self._running:
                        break
                    if msg.data:
                        log.info("message received %s", msg.data)
                        message = Message.from_str(msg.data)
                        self.process_message(message)
                    if self._ready.is_set() is False:
                        self._ready.set()
            except Exception as e:
                log.warn("Unexpected error on stream connection: %s", e)

    def _connect(self) -> SSEClient:
        return SSEClient(self._stream_url, headers={
            'Authorization': f'Bearer {self._token}',
            'API-Key': self._api_key
        })

    def process_message(self, msg: Message) -> None:
        processor: Union[FlagMsgProcessor, SegmentMsgProcessor, None] = None
        if msg.domain == "flag":
            log.debug('Starting flag message processor with %s', msg)
            processor = FlagMsgProcessor(cache=self._cache,
                                         client=self._client,
                                         environment_id=self._environment_id,
                                         msg=msg)
        elif msg.domain == "target-segment":
            log.debug('Starting segment message processor with %s', msg)
            processor = SegmentMsgProcessor(
                cache=self._cache,
                client=self._client,
                environment_id=self._environment_id,
                msg=msg
            )
        if processor:
            processor.start()
            self._msg_processors.append(processor)

    def stop(self):
        log.info("Stopping stream processor and msg processors")
        for processor in self._msg_processors:
            processor.stop()
        self._running = False


class FlagMsgProcessor(Thread):

    def __init__(self, cache: Cache, client: AuthenticatedClient,
                 environment_id: str, msg: Message):
        Thread.__init__(self)
        self._cache = cache
        self._client = client
        self._environemnt_id = environment_id
        self._msg = msg

    def run(self):
        log.debug("Fetching flag config '%s' from server",
                  self._msg.identifier)
        fc = get_feature_config(client=self._client,
                                identifier=self._msg.identifier,
                                environment_uuid=self._environemnt_id)
        log.info("Feature config '%s' loaded", fc.feature)
        if self._msg.event == 'create' or self._msg.event == 'patch':
            self._cache.set(f'flags/{fc.feature}', fc)
            log.info('flag %s successfully stored in the cache', fc.feature)
        elif self._msg.event == 'delete':
            self._cache.remove(f'flags/{fc.feature}')
            log.info('flag %s successfully removed from cache', fc.feature)


class SegmentMsgProcessor(Thread):

    def __init__(self, cache: Cache, client: AuthenticatedClient,
                 environment_id: str, msg: Message):
        Thread.__init__(self)
        self._cache = cache
        self._client = client
        self._environemnt_id = environment_id
        self._msg = msg

    def run(self):
        log.debug("Fetching target segment '%s' from server",
                  self._msg.identifier)
        ts = get_target_segment(client=self._client,
                                identifier=self._msg.identifier,
                                environment_uuid=self._environemnt_id)
        log.info("Target segment '%s' loaded", ts.identifier)
        if self._msg.event == 'create' or self._msg.event == 'patch':
            self._cache.set(f'segments/{ts.identifier}', ts)
            log.info('flag %s successfully stored in cache', ts.identifier)
        elif self._msg.event == 'delete':
            self._cache.remove(f'segments/{ts.identifier}')
            log.info('flag %s successfully removed from cache', ts.identifier)
