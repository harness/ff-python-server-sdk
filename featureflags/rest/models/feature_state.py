from enum import Enum


class FeatureState(str, Enum):
    ON = "on"
    OFF = "off"

    def __str__(self) -> str:
        return str(self.value)
