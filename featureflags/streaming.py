from threading import Thread
import threading
from typing import Any, Callable, Iterable, Mapping, Optional

from featureflags.config import Config
from featureflags.sse_client import SSEClient
from featureflags.util import log


class StreamProcessor(Thread):
    def __init__(self, api_key: str, token: str, config: Config, ready: threading.Event):
        Thread.__init__(self)
        self.daemon = True
        self._running = False
        self._ready = ready
        self._api_key = api_key
        self._token = token
        self._stream_url = f'{config.base_url}/stream'

    def run(self):
        log.info("Starting StreamingProcessor connecting to uri: " + self._stream_url)
        self._running = True

        while self._running:
            try:
                messages = self._connect()
                for msg in messages:
                    if not self._running:
                        break
                    log.info("message received %s", msg)
                    if msg and self._ready.is_set() is False:
                        self._ready.set()
            except Exception as e:
                log.warn("Unexpected error on stream connection: %s", e)
                self.stop()
                break

    def _connect(self) -> SSEClient:
        return SSEClient(self._stream_url, headers={
            'Authorization': f'Bearer {self._token}',
            'API-Key': self._api_key
        })

    def stop(self):
        log.info("Stopping stream processor")
        self._running = False
