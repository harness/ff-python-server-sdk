from threading import Thread
from typing import Any, Callable, Iterable, Mapping, Optional

from featureflags.config import Config
from featureflags.sse_client import SSEClient
from featureflags.util import log


class StreamProcessor(Thread):
    def __init__(self, config: Config):
        super(Thread, self).__init__()
        self.daemon = True
        self._running = False
        self._config = config

    def run(self):
        log.info("Starting StreamingUpdateProcessor connecting to uri: " + self._uri)
        self._running = True

        while self._running:
            try:
                messages = self._connect()
                for msg in messages:
                    log.info("message received", msg)
            except Exception as e:
                log.warn("Unexpected error on stream connection: %s", e)
                self.stop()
                break

    def _connect(self) -> SSEClient:
        return SSEClient(self._config.base_url)

    def stop(self):
        log.info("Stopping stream processor")
        self._running = False
