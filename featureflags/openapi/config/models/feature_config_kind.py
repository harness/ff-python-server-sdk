from enum import Enum


class FeatureConfigKind(str, Enum):
    BOOLEAN = "boolean"
    INT = "int"
    JSON = "json"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
