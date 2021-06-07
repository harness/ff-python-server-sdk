from enum import Enum


class FeatureConfigKind(str, Enum):
    BOOLEAN = "boolean"
    INT = "int"
    STRING = "string"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
