from collections.abc import Callable, Mapping
from datetime import date, datetime

from exodia import ExodiaException, validators
from exodia.utils import logger

__all__ = ("Field", "String", "Integer", "Func", "List", "Exodia", "Date", "DateTime")


class Field:
    """
    Represents a Field

    class Person:
        name = ex.Field()

    except that you don't create Field instances, you create subclasses only.

    :param of_type: represents the allowed types to be worked with during validation process
    """

    of_type = None

    def __init__(self, *args, **kwargs):
        self._name = None
        self.args = args
        self.kwargs = kwargs

        assert self.of_type, "of_type can't be of value None"

        self._validators = [
            self.get_type_validator(),
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

    def _pop_validator(self, v: validators.Validator):
        for i, validator in enumerate(self._validators):
            if validator == v:
                return self._validators.pop(i)

    def _has_validator(self, v):
        return v in self._validators

    def _run_validators(self, value, field_name=None, instance=None):
        errors = []

        for validator in self._validators:
            try:
                validator(value, field_name=field_name, instance=instance)
            except ExodiaException as e:
                errors.append(e)

        if errors:
            raise ExodiaException(errors)

    def _no_validator_of_type(self, v):
        for validator in self._validators:
            if isinstance(validator, v):
                raise ExodiaException(
                    "Can't have validators [{v1}, {v2}] at the same time".format(
                        v1=validator.__class__.__name__,
                        v2=v.__name__,
                    )
                )

    def prepare_for_validation(self, v):
        return v

    def validate(self, value):
        self._run_validators(self.prepare_for_validation(value))
        return self.to_repr(value)

    def get_type_validator(self):
        return validators.Type(self.of_type)

    def to_repr(self, v):
        return v

    def optional(self):
        required = self._pop_validator(validators.Required())
        self._add_validator(validators.Optional())

        if required:
            logger.info("Found an optional() constraint followed by required()")

        # generate an optional self.of_type validator
        current_type_validator = self._pop_validator(self.get_type_validator())
        OptionalTypeValidator = current_type_validator.merge(validators.Type(None))

        self._add_validator(OptionalTypeValidator)
        return self

    def required(self):
        optional = self._pop_validator(validators.Optional())

        if optional:
            logger.info("Found a required() constraint followed by optional()")

        self._add_validator(validators.Required())

        current_type_validator = self._pop_validator(self.get_type_validator())
        RequiredTypeValidator = current_type_validator.__class__(self.of_type)

        self._add_validator(RequiredTypeValidator)
        return self

    def function(self, f, message):
        self._add_validator(validators.Function(f, message))
        return self

    def enum(self, options):
        self._add_validator(validators.Enum(options))
        return self

    def ref(self, field, expr, message=None):
        self._add_validator(validators.Ref(field, expr, message))
        return self

    def reset(self, v):
        self._validators = [
            self.get_type_validator(),
        ]

        return self

    def __set__(self, instance, value):
        self._run_validators(self.prepare_for_validation(value), self._name, instance)
        instance.__dict__[self._name] = self.to_repr(value)

    def __get__(self, instance, owner):
        return instance.__dict__[self._name]


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
        self._add_validator(
            validators.Stack(
                [
                    validators.GreaterThan(value),
                    validators.Equal(value),
                ]
            )
        )

        return self

    def max(self, value: int):
        self._add_validator(
            validators.Stack(
                [
                    validators.LessThan(value),
                    validators.Equal(value),
                ]
            )
        )

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


class Date(Field):
    of_type = [str, date]

    def prepare_for_validation(self, v):
        return date.fromisoformat(v)

    def to_repr(self, v):
        return date.fromisoformat(v)

    def between(self, start: date, end: date):
        self._add_validator(validators.Between(start, end))
        return self

    def before(self, d: date):
        self._add_validator(validators.LessThan(d))
        return self

    def after(self, d: date):
        self._add_validator(validators.GreaterThan(d))
        return self


class DateTime(Date):
    of_type = [str, datetime]

    def prepare_for_validation(self, v: str):
        return datetime.fromisoformat(v)

    def before(self, d: datetime):
        self._add_validator(validators.LessThan(d))
        return self

    def after(self, d: datetime):
        self._add_validator(validators.GreaterThan(d))
        return self

    def between(self, start: datetime, end: datetime):
        self._add_validator(validators.Between(start, end))
        return self
