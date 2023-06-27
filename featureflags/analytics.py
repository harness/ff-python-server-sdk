import time
from threading import Lock, Thread
from typing import Dict, List, Union

import attr

from featureflags.models.metrics_data_metrics_type import \
    MetricsDataMetricsType

from .api.client import AuthenticatedClient
from .api.default.post_metrics import sync_detailed as post_metrics
from .config import Config
from .evaluations.target import Target
from .evaluations.target_attributes import TargetAttributes
from .evaluations.variation import Variation
from .models.key_value import KeyValue
from .models.metrics import Metrics
from .models.metrics_data import MetricsData
from .models.target_data import TargetData
from .models.unset import Unset
from .sdk_logging_codes import info_metrics_thread_started, \
    info_metrics_success, warn_post_metrics_failed, \
    info_metrics_thread_existed, info_metrics_target_exceeded
from .util import log

FF_METRIC_TYPE = 'FFMETRICS'
FEATURE_IDENTIFIER_ATTRIBUTE = 'featureIdentifier'
FEATURE_NAME_ATTRIBUTE = 'featureName'
VARIATION_IDENTIFIER_ATTRIBUTE = 'variationIdentifier'
VARIATION_VALUE_ATTRIBUTE = 'variationValue'
TARGET_ATTRIBUTE = 'target'
SDK_VERSION_ATTRIBUTE = 'SDK_VERSION'
SDK_VERSION = '1.0.0'
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

    def __init__(self, config: Config, client: AuthenticatedClient,
                 environment: str) -> None:
        self._lock = Lock()
        self._config = config
        self._client = client
        self._environment = environment
        self._data: Dict[str, AnalyticsEvent] = {}
        self._target_data: List[Dict[str, MetricTargetData]] = [{}]
        self._max_number_of_batches = 20
        self._max_batch_size = 1000
        self._current_batch_index = 0
        self.max_target_data_exceeded = False

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
            # Store unique evaluation events. We map a unique evaluation
            # event to its count.
            unique_evaluation_key = self.get_key(event)
            if unique_evaluation_key in self._data:
                self._data[unique_evaluation_key].count += 1
            else:
                event.count = 1
                self._data[unique_evaluation_key] = event

            # Store unique targets. If the target already exists
            # just ignore it.
            if event.target is not None and not event.target.anonymous:
                unique_target_key = self.get_target_key(event)
                # TODO - check if key is in any of the batches
                if unique_target_key not in self._target_data:
                    # Temporary workaround for FFM-8231 - limit max size of
                    # target
                    # metrics to 50k, which ff-server can process in around
                    # 18 seconds. This possibly prevent some targets from
                    # getting
                    # registered and showing in the UI, but in theory, they
                    # should get registered eventually on subsequent
                    # evaluations.
                    # We want to eventually use a batching solution
                    # to avoid this.

                    # If we've exceeded the max batch size for the current
                    # batch, then create a new batch and start using it.
                    current_batch = self._target_data[
                        self._current_batch_index]

                    if len(current_batch) >= self._max_batch_size:
                        self._target_data.append({})
                        self._current_batch_index += 1
                        current_batch = self._target_data[
                            self._current_batch_index]

                    target_name = event.target.name
                    # If the target has no name use the identifier
                    if not target_name:
                        target_name = event.target.identifier
                    current_batch[unique_target_key] = MetricTargetData(
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
            for batch in self._target_data:
                for _, unique_target in batch.items():
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
        finally:
            self._data = {}
            self._target_data = {}
            self.max_target_data_exceeded = False
            self._lock.release()

        body: Metrics = Metrics(target_data=target_data,
                                metrics_data=metrics_data)
        response = post_metrics(client=self._client,
                                environment=self._environment, json_body=body)
        log.debug('Metrics server returns: %d', response.status_code)
        if response.status_code >= 400:
            warn_post_metrics_failed(response.status_code)
            return
        info_metrics_success()
        return

    def close(self) -> None:
        self._running = False
        if len(self._data) > 0:
            self._send_data()
        info_metrics_thread_existed()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
