import random
import threading
import time
from threading import Thread
from typing import Union

from tenacity import RetryError

from featureflags.repository import DataProviderInterface
from .api.client import AuthenticatedClient
from .api.default.get_feature_config_by_identifier import \
    sync as get_feature_config
from .api.default.get_segment_by_identifier import sync as get_target_segment
from .config import Config
from .models.message import Message
from .sdk_logging_codes import info_stream_connected, \
    info_stream_event_received, warn_stream_disconnected, \
    warn_stream_retrying, info_stream_stopped, \
    warn_stream_retrying_long_duration, warning_fetch_feature_by_id_failed, \
    warning_fetch_group_by_id_failed, info_polling_stopped, info_poll_started
from .sse_client import SSEClient
from .util import log

BACK_OFF_IN_SECONDS = 5


class StreamProcessor(Thread):
    def __init__(self, repository: DataProviderInterface,
                 client: AuthenticatedClient,
                 environment_id: str, api_key: str, token: str,
                 config: Config,
                 ready: threading.Event,
                 poller: threading.Event,
                 cluster: str):

        Thread.__init__(self)
        self.daemon = True
        self._running = False
        self._ready = ready
        self.poller = poller
        self._client = client
        self._environment_id = environment_id
        self._api_key = api_key
        self._token = token
        self._stream_url = f'{config.base_url}/stream?cluster={cluster}'
        self._repository = repository
        self.reconnect_timer = 0
        self._poll_interval = config.pull_interval
        self._disconnect_notified = False

    def run(self):
        log.info("Starting StreamingProcessor connecting to uri: " +
                 self._stream_url)
        self._running = True
        retries = 0
        while self._running:
            try:
                messages = self._connect()
                info_stream_connected()

                # If this is a reconnection, set this flag back to false
                # so we can notify correctly if we disconnect again.
                self._disconnect_notified = False

                info_polling_stopped('streaming mode is active')
                self.poller.clear()  # were streaming now, so tell any poller
                # threads calling wait to wait...
                self._ready.set()
                retries = 0  # reset the retry counter
                for msg in messages:
                    if not self._running:
                        break
                    if msg.data:
                        info_stream_event_received(msg.data)
                        message = Message.from_str(msg.data)
                        self.process_message(message)
                    if self._ready.is_set() is False:
                        self._ready.set()
            except Exception as e:
                if not self._disconnect_notified:
                    warn_stream_disconnected(e)
                    info_poll_started(self._poll_interval)
                    self._disconnect_notified = True
                else:
                    log.warning("Stream retry failed: %s", str(e))

                self._ready.clear()
                # Signal the poller than it should start due to stream error.
                if self.poller.is_set() is False:
                    self.poller.set()

                # Check if retry attempts have reached a threshold before
                # we log an error to the user
                retry_error_log_threshold = 4
                if retries >= retry_error_log_threshold:
                    warn_stream_retrying_long_duration()

                # Calculate back of sleep
                sleep = (BACK_OFF_IN_SECONDS * 2 ** retries +
                         random.uniform(0, 1))

                warn_stream_retrying(f'{sleep.__str__()}s')
                time.sleep(sleep)
                retries += 1

    def _connect(self) -> SSEClient:
        return SSEClient(url=self._stream_url, headers={
            'Authorization': f'Bearer {self._token}',
            'API-Key': self._api_key
        }, retry=BACK_OFF_IN_SECONDS, verify=self._client.tls_trusted_cas_file)

    def process_message(self, msg: Message) -> None:
        processor: Union[FlagMsgProcessor, SegmentMsgProcessor, None] = None
        if msg.domain == "flag":
            log.debug('Starting flag message processor with %s', msg)
            processor = FlagMsgProcessor(repository=self._repository,
                                         client=self._client,
                                         environment_id=self._environment_id,
                                         msg=msg)
        elif msg.domain == "target-segment":
            log.debug('Starting segment message processor with %s', msg)
            processor = SegmentMsgProcessor(
                repository=self._repository,
                client=self._client,
                environment_id=self._environment_id,
                msg=msg
            )
        if processor:
            processor.start()

    def stop(self):
        self._running = False
        info_stream_stopped()


class FlagMsgProcessor(Thread):

    def __init__(self, repository: DataProviderInterface,
                 client: AuthenticatedClient,
                 environment_id: str, msg: Message):
        Thread.__init__(self)
        self._repository = repository
        self._client = client
        self._environemnt_id = environment_id
        self._msg = msg

    def run(self):
        if self._msg.event == 'create' or self._msg.event == 'patch':
            try:
                log.debug("Fetching flag config '%s' from server",
                          self._msg.identifier)
                fc = get_feature_config(client=self._client,
                                        identifier=self._msg.identifier,
                                        environment_uuid=self._environemnt_id)
                log.debug("Feature config '%s' loaded", fc.feature)
                self._repository.set_flag(fc)
                log.debug('flag %s successfully stored in the cache',
                          fc.feature)

            except RetryError as e:
                last_exception = e.last_attempt.exception()
                if last_exception:
                    warning_fetch_feature_by_id_failed(
                        e.last_attempt.exception())
                else:
                    result_error = e.last_attempt.result()
                    warning_fetch_feature_by_id_failed(result_error)

        elif self._msg.event == 'delete':
            self._repository.remove_flag(self._msg.identifier)
            log.debug('flag %s successfully removed from cache',
                      self._msg.identifier)


class SegmentMsgProcessor(Thread):

    def __init__(self, repository: DataProviderInterface,
                 client: AuthenticatedClient,
                 environment_id: str, msg: Message):
        Thread.__init__(self)
        self._repository = repository
        self._client = client
        self._environemnt_id = environment_id
        self._msg = msg

    def run(self):
        if self._msg.event == 'create' or self._msg.event == 'patch':
            try:
                log.debug("Fetching target segment '%s' from server",
                          self._msg.identifier)
                ts = get_target_segment(client=self._client,
                                        identifier=self._msg.identifier,
                                        environment_uuid=self._environemnt_id)
                log.debug("Target segment '%s' loaded", ts.identifier)
                self._repository.set_segment(ts)
                log.debug('flag %s successfully stored in cache',
                          ts.identifier)

            except RetryError as e:
                last_exception = e.last_attempt.exception()
                if last_exception:
                    warning_fetch_group_by_id_failed(
                        e.last_attempt.exception())
                else:
                    result_error = e.last_attempt.result()
                    warning_fetch_group_by_id_failed(result_error)

        elif self._msg.event == 'delete':
            self._repository.remove_segment(self._msg.identifier)
            log.debug('flag %s successfully removed from cache',
                      self._msg.identifier)
