"""Display-safe formatting for product reports."""

import math
from typing import Any


def display_value(value: Any) -> Any:
    if value is None:
        return "not_available"
    if isinstance(value, str):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(number) or math.isinf(number):
        return "undefined"
    if abs(number) > 999:
        return ">999 or undefined_denominator_near_zero"
    return round(number, 6)


def display_bool(value: Any) -> str:
    return "true" if value is True else "false" if value is False else "not_available"
