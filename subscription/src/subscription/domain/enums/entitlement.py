from enum import StrEnum


class EntitlementValueType(StrEnum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    DECIMAL = "decimal"
    STRING = "string"
    UNLIMITED = "unlimited"
