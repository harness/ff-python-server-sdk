from enum import Enum


class MetricsDataMetricsType(str, Enum):
    FFMETRICS = "FFMETRICS"

    def __str__(self) -> str:
        return str(self.value)
