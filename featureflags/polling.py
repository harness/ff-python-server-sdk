import time
from threading import Event, Thread

from featureflags.api.client import AuthenticatedClient

from .api.default.get_all_segments import sync as retrieve_segments
from .api.default.get_feature_config import sync as retrieve_flags
from .config import Config
from .util import log


class PollingProcessor(Thread):

    def __init__(self, client: AuthenticatedClient, config: Config,
                 environment_id: str, ready: Event,
                 stream_ready: Event) -> None:
        Thread.__init__(self)
        self.daemon = True
        self.__environment_id = environment_id
        self.__client = client
        self.__config = config
        self.__running = False
        self.__ready = ready
        self.__stream_ready = stream_ready

    def run(self):
        if not self.__running:
            log.info("Starting PollingProcessor with request interval: " +
                     str(self.__config.pull_interval))
            self.__running = True
            while self.__running:
                start_time = time.time()
                try:
                    t1 = Thread(target=self.__retrieve_segments)
                    t2 = Thread(target=self.__retrieve_flags)
                    t1.start()
                    t2.start()
                    t1.join()
                    t2.join()
                    if not self.__ready.is_set() is True:
                        log.info("PollingProcessor initialized ok")
                        if self.__config.enable_stream and \
                                not self.__stream_ready.is_set():
                            log.debug('Poller is in pause mode...')
                            self.__ready.wait()
                        else:
                            self.__ready.set()
                except Exception as e:
                    log.exception(
                        'Error: Exception encountered when polling flags. %s',
                        e
                    )

                elapsed = time.time() - start_time
                if elapsed < self.__config.pull_interval:
                    time.sleep(self.__config.pull_interval - elapsed)

    def stop(self):
        log.info("Stopping PollingProcessor")
        self.__running = False

    def __retrieve_flags(self):
        log.debug("Loading feature flags")
        flags = retrieve_flags(
            client=self.__client, environment_uuid=self.__environment_id
        )
        log.debug("Feature flags loaded")
        for flag in flags:
            log.debug("Setting the cache value %s", flag.feature)
            self.__config.cache.set(f"flags/{flag.feature}", flag)

    def __retrieve_segments(self):
        log.debug("Loading target segments")
        segments = retrieve_segments(
            client=self.__client, environment_uuid=self.__environment_id
        )
        log.debug("Target segments loaded")
        for segment in segments:
            log.debug("Setting the cache segment value %s", segment.identifier)
            self.__config.cache.set(f"segments/{segment.identifier}", segment)
