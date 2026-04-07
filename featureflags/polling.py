import time
from concurrent.futures import Future
from threading import Event, Thread
from typing import Dict

from featureflags.repository import DataProviderInterface

from .api import (UnrecoverableRequestException,
                  retryable_retrieve_feature_config,
                  retryable_retrieve_segments)
from .config import Config
from .openapi.config import AuthenticatedClient
from .sdk_logging_codes import (info_poll_ran_successfully, info_poll_started,
                                info_polling_stopped, info_sdk_init_ok,
                                warn_failed_init_fetch_error,
                                warning_fetch_all_features_failed,
                                warning_fetch_all_groups_failed)
from .util import log


class RetrievalError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"RetrievalError: {self.message}"


class PollingProcessor(Thread):
    __initialised_failed_reason: Dict[bool, str]

    def __init__(self, client: AuthenticatedClient, config: Config,
                 environment_id: str, wait_for_initialization: Event,
                 initialised_failed_reason: Dict[bool, str],
                 ready: Event, stream_ready: Event,
                 repository: DataProviderInterface,
                 cluster: str) -> None:
        Thread.__init__(self)
        self.daemon = True
        self.__environment_id = environment_id
        self.__client = client
        self.__config = config
        self.__running = False
        self.__wait_for_initialization = wait_for_initialization
        self.__initialised_failed_reason = initialised_failed_reason
        self.__ready = ready
        self.__stream_ready = stream_ready
        self.__repository = repository
        self.__cluster = cluster

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
                log.info("Initial target segments and flags fetched")
                if not self.__config.enable_stream:
                    info_poll_started(self.__config.pull_interval)

                #  Segments and flags have been cached so
                #  mark the Client as initialised.
                self.__wait_for_initialization.set()
                info_sdk_init_ok()

            except RetrievalError as ex:
                warn_failed_init_fetch_error(ex)
                self.__initialised_failed_reason[True] = str(ex)
                # Unblock the thread and log that initialization has failed
                self.__wait_for_initialization.set()

            except Exception as ex:
                warn_failed_init_fetch_error(ex)
                self.__initialised_failed_reason[True] = str(ex)
                # Unblock the thread and log that initialization has failed
                self.__wait_for_initialization.set()

            if not self.__config.enable_stream:
                # Sleep for an interval before going into the polling loop,
                # as we've just fetched flags/groups on init.
                time.sleep(self.__config.pull_interval)

            while self.__running:
                start_time = time.time()
                try:
                    if self.__config.enable_stream and \
                            self.__stream_ready.is_set():
                        #  Block until ready.set() is called
                        self.__ready.wait()
                        # on stream disconnect, make sure flags are in sync
                        self.retrieve_flags_and_segments()
                        info_poll_ran_successfully()
                        # Reset the start time so we don't do another poll
                        # immediately
                        start_time = time.time()
                    else:
                        self.retrieve_flags_and_segments()
                        info_poll_ran_successfully()
                        self.__ready.set()
                except RetrievalError as ex:
                    log.error('Polling error: %s',
                              ex)
                except Exception as e:
                    log.exception(
                        'Error: Exception encountered when polling flags. %s',
                        e
                    )

                elapsed = time.time() - start_time
                if elapsed < self.__config.pull_interval:
                    log.debug("Poller sleeping for " +
                              (
                                  self.__config.pull_interval -
                                  elapsed).__str__())
                    " seconds"
                    time.sleep(self.__config.pull_interval - elapsed)

    def stop(self):
        self.__running = False
        info_polling_stopped("Client was closed")

    def retrieve_flags_and_segments(self):
        flags_future = Future()
        segments_future = Future()

        flags_thread = Thread(target=self.__retrieve_flags,
                              args=(flags_future,))
        segments_thread = Thread(target=self.__retrieve_segments,
                                 args=(segments_future,))

        flags_thread.start()
        segments_thread.start()

        flags_thread.join()
        segments_thread.join()

        flags_exception = flags_future.exception()
        segments_exception = segments_future.exception()

        if flags_exception:
            raise flags_exception

        if segments_exception:
            raise segments_exception

    def __retrieve_flags(self, future: Future):
        try:
            log.debug("Loading feature flags")
            flags = retryable_retrieve_feature_config(
                client=self.__client, environment_uuid=self.__environment_id,
                cluster=self.__cluster
            ).parsed
            log.debug("Feature flags loaded")
            for flag in flags:
                log.debug("Put flag %s into repository", flag.feature)
                self.__repository.set_flag(flag)
            future.set_result(
                "Success")

        except UnrecoverableRequestException as e:
            warning_fetch_all_features_failed(e)
            future.set_exception(
                RetrievalError(
                    f"Failed to retrieve flags '{e}'"))

        except Exception as e:
            future.set_exception(
                RetrievalError(
                    f"Failed to retrieve flags '{e}'"))

    def __retrieve_segments(self, future: Future):
        try:
            log.debug("Loading target segments")
            segments = retryable_retrieve_segments(
                client=self.__client,
                environment_uuid=self.__environment_id,
                cluster=self.__cluster
            ).parsed
            log.debug("Target segments loaded")
            for segment in segments:
                log.debug("Put %s segment into repository", segment.identifier)
                self.__repository.set_segment(segment)
            future.set_result(
                "Success")

        except UnrecoverableRequestException as e:
            warning_fetch_all_groups_failed(e)
            future.set_exception(
                RetrievalError(
                    f"Failed to retrieve segments '{e}'"))

        except Exception as ex:
            future.set_exception(
                RetrievalError(
                    f"Failed to retrieve segments '{ex}'"))
