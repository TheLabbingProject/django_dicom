from enum import Enum


class NegativityEnum(Enum):
    POSITIVE = 0
    NEGATIVE = 1


class FieldsEnum(Enum):
    NORMAL = 0
    LIST = 1
    STRING = 2


number_lookups = [
    ("exact", "Equals"),
    ("gt", "Greater than"),
    ("gte", "Greater than equal"),
    ("lt", "Less than"),
    ("lte", "Less than equal"),
]
