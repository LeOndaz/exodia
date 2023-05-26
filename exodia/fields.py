import typing
from collections.abc import Callable, Mapping
from datetime import date, datetime

from typing_extensions import Self

from exodia import ExodiaException, validators

__all__ = ("Field", "String", "Integer", "Func", "List", "Exodia", "Date", "DateTime")

T = typing.TypeVar("T")


class Field(typing.Generic[T]):
    """
    Represents a Field

    class Person:
        name = ex.Field()

    except that you don't create Field instances, you create subclasses only.

    :param of_type: represents the allowed types to be worked with during validation process
    """

    of_type: typing.Any = None

    def __init__(self, *args, **kwargs):
        self._name = None
        self.args = args
        self.kwargs = kwargs
        self._validators = []

        assert self.of_type, "of_type can't be of value None"
        self.reset()

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

    def prepare_for_validation(self, v: typing.Any) -> T:
        return v

    def validate(self, value) -> T:
        self._run_validators(self.prepare_for_validation(value))
        return self.to_repr(value)

    def get_type_validator(self):
        return validators.Type(self.of_type)

    def to_repr(self, v) -> T:
        return v

    def optional(self) -> Self:
        self._pop_validator(validators.Required())
        self._add_validator(validators.Optional())

        # generate an optional self.of_type validator
        current_type_validator = self._pop_validator(self.get_type_validator())
        OptionalTypeValidator = current_type_validator.merge(validators.Type(None))

        self._add_validator(OptionalTypeValidator)
        return self

    def required(self) -> Self:
        self._pop_validator(validators.Optional())
        self._add_validator(validators.Required())

        current_type_validator = self._pop_validator(self.get_type_validator())
        RequiredTypeValidator = current_type_validator.__class__(self.of_type)

        self._add_validator(RequiredTypeValidator)
        return self

    def function(self, f, message) -> Self:
        self._add_validator(validators.Function(f, message))
        return self

    def enum(self, options) -> Self:
        self._add_validator(validators.Enum(options))
        return self

    def ref(self, field, expr, message=None) -> Self:
        self._add_validator(validators.Ref(field, expr, message))
        return self

    def reset(self):
        self._validators = [
            self.get_type_validator(),
        ]

    def __set__(self, instance, value) -> None:
        self._run_validators(self.prepare_for_validation(value), self._name, instance)
        instance.__dict__[self._name] = self.to_repr(value)

    def __get__(self, instance, owner) -> T:
        return instance.__dict__[self._name]


class String(Field[str]):
    of_type: typing.Any = str

    def __init__(self, length=None, **kwargs):
        super().__init__(length, **kwargs)

        if length:
            self._add_validator(validators.Length(length))

    def min(self, value: int) -> Self:
        self._add_validator(validators.MinLength(value))
        return self

    def max(self, value: int) -> Self:
        self._add_validator(validators.MaxLength(value))
        return self

    def not_empty(self) -> Self:
        self._add_validator(validators.NotEmpty())
        return self


class Integer(Field[int]):
    of_type: typing.Any = int

    def min(self, value: int) -> Self:
        self._add_validator(
            validators.Stack(
                [
                    validators.GreaterThan(value),
                    validators.Equal(value),
                ]
            )
        )

        return self

    def max(self, value: int) -> Self:
        self._add_validator(
            validators.Stack(
                [
                    validators.LessThan(value),
                    validators.Equal(value),
                ]
            )
        )

        return self

    def between(self, min: int, max: int) -> Self:
        self._add_validator(validators.Between(min, max))
        return self

    def multiple_of(self, n) -> Self:
        self._add_validator(validators.MultipleOf(n))
        return self


class List(String, Field[typing.List]):
    of_type: typing.Any = list


class Func(Field[typing.Callable]):
    of_type: typing.Any = Callable


class Exodia(Field[typing.Mapping]):
    of_type: typing.Any = Mapping

    def __init__(self, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_validator(validators.Exodia(schema))


class DateTime(Field[datetime]):
    of_type = [str, datetime]

    def prepare_for_validation(self, v: str) -> datetime:
        return datetime.fromisoformat(v)

    def before(self, d: datetime) -> Self:
        self._add_validator(validators.LessThan(d))
        return self

    def after(self, d: datetime) -> Self:
        self._add_validator(validators.GreaterThan(d))
        return self

    def between(self, start: datetime, end: datetime) -> Self:
        self._add_validator(validators.Between(start, end))
        return self


class Date(DateTime, Field[date]):
    of_type = [str, date]

    def prepare_for_validation(self, v) -> date:
        return date.fromisoformat(v)

    def to_repr(self, v) -> date:
        return date.fromisoformat(v)

    def between(self, start: date, end: date) -> Self:
        self._add_validator(validators.Between(start, end))
        return self

    def before(self, d: date) -> Self:
        self._add_validator(validators.LessThan(d))
        return self

    def after(self, d: date) -> Self:
        self._add_validator(validators.GreaterThan(d))
        return self


class Any(Field[T]):
    of_type = object

    def of(self, *fields) -> Self:
        self._add_validator(validators.Any(fields))
        return self
