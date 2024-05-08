import concurrent.futures
import time
import traceback
from threading import Lock, Thread
from typing import Dict, List, Set, Union

import attr
import httpx

from .config import Config
from .openapi.config import AuthenticatedClient
from .openapi.config.models.target import Target
from .openapi.config.models.target_attributes import TargetAttributes
from .openapi.config.models.variation import Variation
from .openapi.metrics.api.metrics.post_metrics import \
    sync_detailed as post_metrics
from .openapi.metrics.models.key_value import KeyValue
from .openapi.metrics.models.metrics import Metrics
from .openapi.metrics.models.metrics_data import MetricsData
from .openapi.metrics.models.metrics_data_metrics_type import \
    MetricsDataMetricsType
from .openapi.metrics.models.target_data import TargetData
from .openapi.metrics.types import Unset
from .sdk_logging_codes import (info_evaluation_metrics_exceeded,
                                info_metrics_success,
                                info_metrics_target_batch_success,
                                info_metrics_target_exceeded,
                                info_metrics_thread_existed,
                                info_metrics_thread_started,
                                warn_post_metrics_failed,
                                warn_post_metrics_target_batch_failed)
from .util import log

FF_METRIC_TYPE = 'FFMETRICS'
FEATURE_IDENTIFIER_ATTRIBUTE = 'featureIdentifier'
FEATURE_NAME_ATTRIBUTE = 'featureName'
VARIATION_IDENTIFIER_ATTRIBUTE = 'variationIdentifier'
VARIATION_VALUE_ATTRIBUTE = 'variationValue'
TARGET_ATTRIBUTE = 'target'
SDK_VERSION_ATTRIBUTE = 'SDK_VERSION'
SDK_VERSION = '1.6.1'
SDK_TYPE_ATTRIBUTE = 'SDK_TYPE'
SDK_TYPE = 'server'
SDK_LANGUAGE_ATTRIBUTE = 'SDK_LANGUAGE'
SDK_LANGUAGE = 'python'
GLOBAL_TARGET = 'global'


@attr.s(auto_attribs=True)
class AnalyticsEvent(object):
    target: Target
    flag_identifier: str
    variation: Variation
    count: int = 0


@attr.s(auto_attribs=True)
class MetricTargetData(object):
    identifier: str
    name: str
    attributes: Union[Unset, TargetAttributes] = Unset


class AnalyticsService(object):

    def __init__(self, config: Config,
                 client: AuthenticatedClient,
                 environment: str,
                 cluster: str) -> None:
        self._lock = Lock()
        self._config = config
        self._client = client
        self._environment = environment
        self._cluster = cluster

        # Evaluation metrics
        self._data: Dict[str, AnalyticsEvent] = {}
        # This allows for up to 2K flags with 5 variations each per interval
        self._max_evaluation_metrics = 10000
        self._max_evaluation_metrics_exceeded = False

        # Target metrics - batch based
        self._target_data_batches: List[Dict[str, MetricTargetData]] = [{}]

        # This allows for 100k unique targets per interval
        self._max_number_of_target_batches = 100
        self._max_target_batch_size = 1000
        self._current_target_batch_index = 0
        self.max_target_data_exceeded = False

        # Allow us to track targets for the life of the SDK instance, to
        # prevent sending the same target more than once. This also helps
        # unique targets get processed each interval, because duplicate
        # targets are not making up the 100K limit.
        self._seen_targets: Set[str] = set()

        self._running = False
        self._runner = Thread(target=self._sync)
        self._runner.daemon = True
        self._runner.start()

    def enqueue(self, target: Target, identifier: str,
                variation: Variation):
        event: AnalyticsEvent = AnalyticsEvent(
            target=target,
            flag_identifier=identifier,
            variation=variation
        )

        self._lock.acquire()
        try:
            # Check if adding a new metric would exceed the 10,000 limit
            if len(self._data) < self._max_evaluation_metrics:

                # Store unique evaluation events. We map a unique evaluation
                # event to its count.
                unique_evaluation_key = self.get_key(event)
                if unique_evaluation_key in self._data:
                    self._data[unique_evaluation_key].count += 1
                else:
                    event.count = 1
                    self._data[unique_evaluation_key] = event
            else:
                if not self._max_evaluation_metrics_exceeded:
                    self._max_evaluation_metrics_exceeded = True
                    info_evaluation_metrics_exceeded()

            # Don't store this target if it is anonymous. Note, we currently
            # don't do this check above for evaluation metrics, because we use
            # the global target.
            if target.anonymous:
                return

            unique_target_key = self.get_target_key(event)

            # If we've seen this target before, don't process it
            if unique_target_key in self._seen_targets:
                return

            self._seen_targets.add(unique_target_key)

            # Check if we're on our final target batch - if we are, and we've
            # exceeded the max batch size just return early.
            if len(self._target_data_batches) >= \
                    self._max_number_of_target_batches:
                if len(self._target_data_batches[
                    self._current_target_batch_index]) >= \
                        self._max_target_batch_size:
                    if not self.max_target_data_exceeded:
                        self.max_target_data_exceeded = True
                        info_metrics_target_exceeded()
                    return

            if event.target is not None and not event.target.anonymous:

                # Store unique targets. If the target already exists
                # in any of the batches, don't continue processing it
                for batch in self._target_data_batches:
                    if unique_target_key in batch:
                        return

                # If we've exceeded the max batch size for the current
                # batch, then create a new batch and start using it.
                if len(self._target_data_batches[
                    self._current_target_batch_index]) >= \
                        self._max_target_batch_size:
                    self._target_data_batches.append({})
                    self._current_target_batch_index += 1

                target_name = event.target.name
                # If the target has no name use the identifier
                if not target_name:
                    target_name = event.target.identifier
                self._target_data_batches[
                    self._current_target_batch_index][unique_target_key] = \
                    MetricTargetData(
                        identifier=event.target.identifier,
                        name=target_name,
                        attributes=event.target.attributes
                )

        finally:
            self._lock.release()

    # Returns a key for unique evaluations events.
    def get_key(self, event: AnalyticsEvent) -> str:
        return '{feature}-{variation}-{value}-{target}'.format(
            feature=event.flag_identifier,
            variation=event.variation.identifier,
            value=event.variation.value,
            target=GLOBAL_TARGET,
        )

    # Returns a key for unique targets. Targets are considered unique
    # if they have different identifiers.
    def get_target_key(self, event: AnalyticsEvent) -> str:
        return event.target.identifier

    def _sync(self) -> None:
        if not self._running:
            info_metrics_thread_started(
                f'{self._config.events_sync_interval}s')
            self._running = True
            while self._running:
                time.sleep(self._config.events_sync_interval)
                self._send_data()

    def _send_data(self) -> None:
        if not bool(self._data):
            log.debug('No metrics data!')
            return
        log.debug('Start sending metrics data')
        self._lock.acquire()
        target_data: List[TargetData] = []
        metrics_data: List[MetricsData] = []
        try:
            for _, event in self._data.items():
                metric_attributes: List[KeyValue] = [
                    KeyValue(FEATURE_IDENTIFIER_ATTRIBUTE,
                             event.flag_identifier),
                    KeyValue(FEATURE_NAME_ATTRIBUTE,
                             event.flag_identifier),
                    KeyValue(VARIATION_IDENTIFIER_ATTRIBUTE,
                             event.variation.identifier),
                    KeyValue(VARIATION_VALUE_ATTRIBUTE, event.variation.value),
                    KeyValue(SDK_TYPE_ATTRIBUTE, SDK_TYPE),
                    KeyValue(SDK_LANGUAGE_ATTRIBUTE, SDK_LANGUAGE),
                    KeyValue(SDK_VERSION_ATTRIBUTE, SDK_VERSION),
                    KeyValue(TARGET_ATTRIBUTE, GLOBAL_TARGET)
                ]

                md = MetricsData(
                    timestamp=int(round(time.time() * 1000)),
                    count=event.count,
                    metrics_type=MetricsDataMetricsType.FFMETRICS,
                    attributes=metric_attributes
                )
                metrics_data.append(md)
            for _, unique_target in self._target_data_batches[0].items():
                self.process_target(target_data, unique_target)

            target_data_batches: List[List[TargetData]] = []
            target_data_batch_index = 0
            # We've already accounted for the first batch, so start processing
            # from the second batch onwards
            for batch in self._target_data_batches[1:]:
                target_data_batches.append([])
                for _, unique_target in batch.items():
                    self.process_target(
                        target_data_batches[target_data_batch_index],
                        unique_target)
                target_data_batch_index += 1

        finally:
            self._data = {}
            self._target_data_batches = [{}]
            self._current_target_batch_index = 0
            self.max_target_data_exceeded = False
            self._max_evaluation_metrics_exceeded = False
            self._lock.release()

        body: Metrics = Metrics(target_data=target_data,
                                metrics_data=metrics_data)
        try:
            response = post_metrics(client=self._client,
                                    environment_uuid=self._environment,
                                    body=body,
                                    cluster=self._cluster)

            log.debug('Metrics server returns: %d', response.status_code)
            if response.status_code >= 400:
                warn_post_metrics_failed(response.status_code)
                return
            if len(target_data_batches) > 0:
                log.info('Sending %s target batches to metrics',
                         len(target_data_batches))
                unique_responses_codes = {}

                # Process batches concurrently
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = []
                    for batch in target_data_batches:
                        # Staggering requests over 0.02 seconds mean that we
                        # will send 200 requests every four seconds, so that
                        # the backend isn't hit too hard.
                        time.sleep(0.02)
                        future = executor.submit(
                            self.process_target_data_batch,
                            batch)
                        futures.append(future)

                    # Wait for all batches to complete
                    concurrent.futures.wait(futures)

                    # Get unique status codes
                    for future in futures:
                        status_code = future.result()
                        if status_code in unique_responses_codes:
                            unique_responses_codes[status_code] += 1
                        else:
                            unique_responses_codes[status_code] = 1

                # Log any error codes
                for unique_code, count in unique_responses_codes.items():
                    if unique_code >= 400:
                        warn_post_metrics_target_batch_failed(
                            f'{count} batches received code {unique_code}')
                        continue
                    info_metrics_target_batch_success(
                        f'{count} batches successful')

            info_metrics_success()
        except httpx.RequestError as ex:
            print(traceback.format_exc())
            warn_post_metrics_failed(ex)

    def process_target_data_batch(self, target_data_batch):
        batch_request_body: Metrics = Metrics(
            target_data=target_data_batch, metrics_data=[]
        )
        response = post_metrics(
            client=self._client, environment=self._environment,
            json_body=batch_request_body
        )
        return response.status_code

    def process_target(self, target_data, unique_target):
        target_attributes: List[KeyValue] = []
        if not isinstance(unique_target.attributes, Unset):
            for key, value in unique_target.attributes.items():
                # Attribute values need to be sent as string to
                # ff-server so convert all values to strings.
                target_attributes.append(KeyValue(key, str(value)))
        td = TargetData(
            identifier=unique_target.identifier,
            name=unique_target.name,
            attributes=target_attributes
        )
        target_data.append(td)

    def is_target_seen(self, target: AnalyticsEvent) -> bool:
        unique_target_key = self.get_target_key(target)

        with self._lock:
            seen = unique_target_key in self._seen_targets
        return seen

    def close(self) -> None:
        self._running = False
        if len(self._data) > 0:
            self._send_data()
        info_metrics_thread_existed()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
