import time
from threading import Lock, Thread
from typing import Dict, List

import attr

from featureflags.models.metrics_data_metrics_type import \
    MetricsDataMetricsType

from .api.client import AuthenticatedClient
from .api.default.post_metrics import sync_detailed as post_metrics
from .config import Config
from .evaluations.feature import FeatureConfig
from .evaluations.target import Target
from .evaluations.variation import Variation
from .models.key_value import KeyValue
from .models.metrics import Metrics
from .models.metrics_data import MetricsData
from .models.target_data import TargetData
from .models.unset import Unset
from .util import log

FF_METRIC_TYPE = 'FFMETRICS'
FEATURE_IDENTIFIER_ATTRIBUTE = 'featureIdentifier'
FEATURE_NAME_ATTRIBUTE = 'featureName'
VARIATION_IDENTIFIER_ATTRIBUTE = 'variationIdentifier'
VARIATION_VALUE_ATTRIBUTE = 'featureValue'
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
    feature_config: FeatureConfig
    variation: Variation
    count: int = 0


class AnalyticsService(object):

    def __init__(self, config: Config, client: AuthenticatedClient,
                 environment: str) -> None:
        self._lock = Lock()
        self._config = config
        self._client = client
        self._environment = environment
        self._data: Dict[str, AnalyticsEvent] = {}

        self._running = False
        self._runner = Thread(target=self._sync)
        self._runner.daemon = True
        self._runner.start()

    def enqueue(self, target: Target, feature_config: FeatureConfig,
                variation: Variation):
        event: AnalyticsEvent = AnalyticsEvent(
            target=target,
            feature_config=feature_config,
            variation=variation
        )

        self._lock.acquire()
        try:
            key = self.get_key(event)
            if key in self._data:
                self._data[key].count += 1
            else:
                event.count = 1
                self._data[key] = event
        finally:
            self._lock.release()

    def get_key(self, event: AnalyticsEvent) -> str:
        return '{feature}-{variation}-{value}-{target}'.format(
            feature=event.feature_config.feature,
            variation=event.variation.identifier,
            value=event.variation.value,
            target=GLOBAL_TARGET,
        )

    def _sync(self) -> None:
        if not self._running:
            log.info("Starting AnalyticsService with request interval: %d",
                     self._config.events_sync_interval)
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
                if event.target is not None and not event.target.anonymous:
                    target_attributes: List[KeyValue] = []
                    if not isinstance(event.target.attributes, Unset):
                        for key, value in event.target.attributes:
                            target_attributes.append(KeyValue(key, value))
                    target_name = event.target.identifier
                    if event.target.name:
                        target_name = event.target.name

                    td = TargetData(
                        identifier=event.target.identifier,
                        name=target_name,
                        attributes=target_attributes
                    )
                    target_data.append(td)

                metric_attributes: List[KeyValue] = [
                    KeyValue(FEATURE_IDENTIFIER_ATTRIBUTE,
                             event.feature_config.feature),
                    KeyValue(FEATURE_NAME_ATTRIBUTE,
                             event.feature_config.feature),
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
        finally:
            self._data = {}
            self._lock.release()
        body: Metrics = Metrics(target_data=target_data,
                                metrics_data=metrics_data)
        response = post_metrics(client=self._client,
                                environment=self._environment, json_body=body)
        log.debug('Metrics server returns: %d', response.status_code)
        if response.status_code >= 400:
            log.error(
                'Error while sending metrics data with status code: %d',
                response.status_code
            )
            return
        log.info('Metrics data sent to server')
        return

    def close(self) -> None:
        self._running = False
        if len(self._data) > 0:
            self._send_data()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
