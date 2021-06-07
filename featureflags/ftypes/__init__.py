from .boolean import Boolean
from .string import String
from .integer import Integer
from .number import Number
from .json import JSON


OPERATORS: dict = {
    bool: Boolean,
    str: String,
    int: Integer,
    float: Number,
    dict: JSON
}
