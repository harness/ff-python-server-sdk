import time
from threading import Event, Thread

from featureflags.api.client import AuthenticatedClient
from featureflags.repository import DataProviderInterface

from .api.default.get_all_segments import sync as retrieve_segments
from .api.default.get_feature_config import sync as retrieve_flags
from .config import Config
from .util import log


class PollingProcessor(Thread):

    def __init__(self, client: AuthenticatedClient, config: Config,
                 environment_id: str, wait_for_initialization: Event,
                 ready: Event, stream_ready: Event,
                 repository: DataProviderInterface) -> None:
        Thread.__init__(self)
        self.daemon = True
        self.__environment_id = environment_id
        self.__client = client
        self.__config = config
        self.__running = False
        self.__wait_for_initialization = wait_for_initialization
        self.__ready = ready
        self.__stream_ready = stream_ready
        self.__repository = repository

    def run(self):
        if not self.__running:
            if self.__config.pull_interval < 60:
                log.warning("Pull Interval must be greater than or equal to "
                            "60 seconds, was: " +
                            str(self.__config.pull_interval) +
                            " setting to 60")
                self.__config.pull_interval = 60

            self.__running = True
            #  Get initial flags and groups
            try:
                log.info("Fetching initial target segments and flags")
                self.retrieve_flags_and_segments()
                log.info("Initial target segments and flags fetched. "
                         "PollingProcessor will start in: " +
                         str(self.__config.pull_interval) + " seconds")
                #  Segments and flags have been cached so
                #  mark the Client as initialised.
                self.__wait_for_initialization.set()
                log.debug("CfClient initialized")
            except Exception as ex:
                log.exception(
                    'Error: Exception encountered when '
                    'getting initial flags and segments. %s',
                    ex
                )
            #  Sleep for an interval before going into the polling loop.
            time.sleep(self.__config.pull_interval)
            log.info("Starting PollingProcessor with request interval: " +
                     str(self.__config.pull_interval))
            while self.__running:
                start_time = time.time()
                try:
                    if self.__config.enable_stream and \
                            self.__stream_ready.is_set():
                        log.debug('Poller will be paused because' +
                                  ' streaming mode is active')
                        # on stream disconnect, make sure flags are in sync
                        self.retrieve_flags_and_segments()
                        #  Block until ready.set() is called
                        self.__ready.wait()
                        log.debug('Poller resuming ')
                    else:
                        self.retrieve_flags_and_segments()
                        self.__ready.set()
                except Exception as e:
                    log.exception(
                        'Error: Exception encountered when polling flags. %s',
                        e
                    )

                elapsed = time.time() - start_time
                if elapsed < self.__config.pull_interval:
                    log.info("Poller sleeping for " +
                             (self.__config.pull_interval - elapsed).__str__())
                    " seconds"
                    time.sleep(self.__config.pull_interval - elapsed)

    def stop(self):
        log.info("Stopping PollingProcessor")
        self.__running = False

    def retrieve_flags_and_segments(self):
        t1 = Thread(target=self.__retrieve_segments)
        t2 = Thread(target=self.__retrieve_flags)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def __retrieve_flags(self):
        log.debug("Loading feature flags")
        flags = retrieve_flags(
            client=self.__client, environment_uuid=self.__environment_id
        )
        log.debug("Feature flags loaded")
        for flag in flags:
            log.debug("Put flag %s into repository", flag.feature)
            self.__repository.set_flag(flag)

    def __retrieve_segments(self):
        log.debug("Loading target segments")
        segments = retrieve_segments(
            client=self.__client, environment_uuid=self.__environment_id
        )
        log.debug("Target segments loaded")
        for segment in segments:
            log.debug("Put %s segment into repository", segment.identifier)
            self.__repository.set_segment(segment)
