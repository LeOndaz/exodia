from typing import Any, Mapping

__all__ = ("ExodiaException",)


class ExodiaException(Exception):
    """An exception to raise when an Exodia validation error happens"""

    def _is_valid_error_value(self, value):
        assert not isinstance(value, Mapping), "value can't be a mapping"
        return isinstance(value, self.__class__)

    def _validate_error_mapping(self, mapping: Mapping):
        errors = []

        for key, value in mapping.items():
            if isinstance(value, Mapping):
                errors += self._validate_error_mapping(value)
            else:
                if not self._is_valid_error_value(value):
                    errors.append(
                        {key: "value {v} is not an exception type!".format(v=v)}
                    )

        return errors

    def __init__(self, data: Any):
        self.data = data

        if isinstance(data, Mapping):
            errors = self._validate_error_mapping(data)
        else:
            errors = data

        super().__init__(errors)
