from typing import Mapping

from exodia import Field


def get_field_attrs(data) -> Mapping:
    result = {}

    for key, value in data.items():
        if isinstance(value, Field):
            result[key] = value

    return result
