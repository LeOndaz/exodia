from collections.abc import Callable, Mapping
from exodia import validators, ExodiaException


class Field:
    of_type = None

    def __init__(self, *args, **kwargs):
        # validator args, validator kwargs
        self._name = None
        self.args = args
        self.kwargs = kwargs

        assert self.of_type, "of_type can't be of value None"

        self._validators = [
            validators.Type(self.of_type),
        ]

    def __set_name__(self, owner, name):
        self._name = name

    def _add_validator(self, v: validators.Validator):
        for validator in self._validators:
            if validator == v:
                raise ExodiaException(
                    "You can't have multiple validators of type {t}".format(
                        t=v.__class__.__name__,
                    )
                )

        self._validators.append(v)

    def _has_validator(self, v):
        return v in self._validators

    def _run_validators(self, value, field_name=None, instance=None):
        for validator in self._validators:
            validator(value, field_name=field_name, instance=instance)

    def _no_validator_of_type(self, v):
        for validator in self._validators:
            if isinstance(validator, v):
                raise ExodiaException(
                    "Can't have validators [{v1}, {v2}] at the same time".format(
                        v1=validator.__class__.__name__,
                        v2=v.__name__,
                    )
                )

    def validate(self, value):
        self._run_validators(value)

    def optional(self):
        self._no_validator_of_type(validators.Required)
        self._add_validator(validators.Optional())
        return self

    def required(self):
        self._no_validator_of_type(validators.Optional)
        self._add_validator(validators.Required())
        return self

    def enum(self, options):
        self._add_validator(validators.Enum(options))
        return self

    def __set__(self, instance, value):
        self._run_validators(value, self._name, instance)
        instance.__dict__[self._name] = value

    def __get__(self, instance, owner):
        return self.of_type(instance.__dict__[self._name])


class String(Field):
    of_type = str

    def __init__(self, length=None, **kwargs):
        super().__init__(length, **kwargs)

        if length:
            self._add_validator(validators.Length(length))

    def min(self, value: int):
        self._add_validator(validators.MinLength(value))
        return self

    def max(self, value: int):
        self._add_validator(validators.MaxLength(value))
        return self

    def not_empty(self):
        self._add_validator(validators.NotEmpty())


class Integer(Field):
    of_type = int

    def min(self, value: int):
        self._add_validator(validators.MinValue(value))
        return self

    def max(self, value: int):
        self._add_validator(validators.MaxValue(value))
        return self

    def between(self, min: int, max: int):
        self._add_validator(validators.Between(min, max))
        return self

    def multiple_of(self, n):
        self._add_validator(validators.MultipleOf(n))
        return self


class List(String):
    of_type = list


class Func(Field):
    of_type = Callable


class Exodia(Field):
    of_type = Mapping

    def __init__(self, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_validator(validators.Exodia(schema))
