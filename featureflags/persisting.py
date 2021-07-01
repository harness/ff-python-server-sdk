import time
from threading import Thread

from .config import Config
from .util import log


class PersistingProcessor(Thread):

    def __init__(self, config: Config, ready: bool) -> None:
        Thread.__init__(self)
        self.daemon = True
        self._config = config
        self._running = False
        self._ready = ready

    def run(self):
        if not self._running:
            log.info("Starting PersistingProcessor with request interval: %d",
                     self._config.pull_interval)
            self._running = True
            while self._running:
                start_time = time.time()
                try:
                    all_data = self._requester.get_all_data()
                    self._store.init(all_data)
                    if not self._ready.is_set() is True \
                            and self._store.initialized is True:
                        log.info("PersistingProcessor initialized ok")
                        self._ready.set()
                except Exception as e:
                    log.exception(
                        'Error: Exception encountered when updating flags. %s',
                        e
                    )

                elapsed = time.time() - start_time
                if elapsed < self._config.poll_interval:
                    time.sleep(self._config.poll_interval - elapsed)

    def stop(self):
        log.info("Stopping PersistingProcessor")
        self._running = False
