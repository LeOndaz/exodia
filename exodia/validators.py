from collections.abc import Callable, Iterable, Mapping
from typing import List

from exodia import ExodiaException
from exodia.utils import get_callable_params

__all__ = (
    "Validator",
    "Stack",
    "LessThan",
    "GreaterThan",
    "Equal",
    "MaxLength",
    "MinLength",
    "Length",
    "Exodia",
    "Type",
    "NotEmpty",
    "Optional",
    "Required",
    "Enum",
    "Between",
    "Function",
    "Ref",
    "MultipleOf",
)


class Validator:
    field_message = "You've forgot to include a message for validator {class_name}"
    generic_message = "You've forgot to include a message for validator {class_name}"

    def validate(self, value, field_name=None, instance=None):
        return False

    def __call__(self, value, field_name=None, instance=None):
        if not self.validate(value, field_name, instance):
            kw = self.get_format_params(value)
            self.fail(field_name, value=value, instance=instance, **kw)

    def __eq__(self, v):
        return isinstance(v, self.__class__)

    def __add__(self, other):
        return None

    def __radd__(self, other):
        return self + other

    def get_format_params(self, value):
        parameter_names = get_callable_params(self.__class__)
        values = []

        for parameter in parameter_names:
            values.append(getattr(self, parameter))

        format_params = dict(zip(parameter_names, values))
        format_params.update({"class_name": self.__class__.__name__})

        return format_params

    def get_message(self, field_name):
        return self.field_message if field_name else self.generic_message

    def fail(self, field_name=None, value=None, **kw):
        message = self.get_message(field_name)

        raise ExodiaException(
            message.format(
                field_name=field_name,
                value=value,
                **kw,
            )
        )


class Required(Validator):
    field_message = "{field_name} is required"
    generic_message = "got None, but a value is required"

    def validate(self, value, field_name=None, instance=None):
        return value is not None


class Optional(Validator):
    """Does nothing"""

    def validate(self, value, field_name=None, instance=None):
        return True


class Length(Validator):
    field_message = "{field_name} must be of length {length}"
    generic_message = "Length must be {length}"

    def __init__(self, length):
        assert isinstance(length, int), "length must be a instance of int"

        self.length = length
        super().__init__()

    def __eq__(self, v):
        return object.__eq__(self, v) and v.length == self.length

    def validate(self, value, field_name=None, instance=None):
        return len(value) == self.length


class NotEmpty(Validator):
    field_message = "{field_name} must not be empty"
    generic_message = "value can't be empty"

    def validate(self, value, field_name=None, instance=None):
        return len(value) == 0


class Between(Validator):
    field_message = "{field_name} must be between ({min}, {max})"
    generic_message = "{value} is not between ({min}, {max})"

    def __init__(self, min, max):
        super().__init__()
        self.min = min
        self.max = max

    def validate(self, value, field_name=None, instance=None):
        return self.min <= value <= self.max


class Type(Validator):
    generic_message = (
        "{value} is of type {actual_type}, expected types {expected_types}"
    )
    field_message = (
        "{field_name}={value} is of type {actual_type}, expected types {expected_types}"
    )

    def __init__(self, ts):
        if not isinstance(ts, Iterable):
            ts = [ts]

        # a hack to support "None" as a type instead of an instance of NoneType, just for convenience
        for i, t in enumerate(ts):
            assert isinstance(t, type) or t is None, "{}.t must be a class".format(
                self.__class__.__name__
            )

            if t is None:
                ts[i] = type(None)

        self.ts = ts
        super().__init__()

    def merge(self, v):
        return self.__class__(ts=self.ts + v.ts)

    def validate(self, value, field_name=None, instance=None):
        return isinstance(value, tuple(self.ts))

    def get_format_params(self, value):
        return dict(
            **super().get_format_params(value),
            actual_type=type(value).__name__,
            expected_types=", ".join(item.__name__ for item in self.ts),
        )


class MultipleOf(Validator):
    generic_message = "{value} is not a multiple of {n}"
    field_message = "{field_name}={value} is not a multiple of {n}"

    def __init__(self, n):
        assert isinstance(n, int), "{}.n must be an instance of integer".format(
            self.__class__.__name__
        )

        super().__init__()
        self.n = n

    def validate(self, value, field_name=None, instance=None):
        return value % self.n == 0

    def __eq__(self, v):
        return isinstance(v, self.__class__) and self.n == v.n


class Enum(Validator):
    field_message = (
        "{value} is not a valid choice for {field_name}, choices are {options}"
    )
    generic_message = "{value} is not a valid choice, choices are {options}"

    def __init__(self, options):
        assert isinstance(options, Iterable) and not isinstance(
            options, Mapping
        ), "{}.options must be a tuple-like object"

        self.options = options
        super().__init__()

    def validate(self, value, field_name=None, instance=None):
        return value in self.options


class MinLength(Validator):
    field_message = (
        "{class_name}.{field_name}={value} must have length greater than {length}"
    )
    generic_message = "{value} must have length greater than {length}"

    def __init__(self, length):
        assert isinstance(length, int), "{}.length must be an instance of str".format(
            self.__class__.__name__
        )

        super().__init__()
        self.length = length

    def validate(self, value, field_name=None, instance=None):
        return len(value) >= self.length


class MaxLength(Validator):
    field_message = "{class_name}{field_name}={value} must have length less than {l}"
    generic_message = "{value} must have length less than {l}"

    def __init__(self, length):
        assert isinstance(length, int), "{}.length must be an instance of str".format(
            self.__class__.__name__
        )

        super().__init__()
        self.length = length

    def validate(self, value, field_name=None, instance=None):
        return len(value) <= self.length


class LessThan(Validator):
    field_message = "{class_name}.{field_name}={value} must be less than {v}"
    generic_message = "{value} must be less than {v}"

    def __init__(self, v):
        super().__init__()
        self.v = v

    def validate(self, value, field_name=None, instance=None):
        return value < self.v


class Equal(Validator):
    field_message = "{class_name}.{field_name}={value} must be equal to {v}"
    generic_message = "{value} must be equal to {v}"

    def __init__(self, v):
        super().__init__()
        self.v = v

    def validate(self, value, field_name=None, instance=None):
        return value == self.v


class GreaterThan(Validator):
    field_message = "{class_name}.{field_name}={value} must be greater than {v}"
    generic_message = "{value} must be greater than {v}"

    def __init__(self, v):
        super().__init__()
        self.v = v

    def validate(self, value, field_name=None, instance=None):
        return value > self.v


class Exodia(Validator):
    def __init__(self, schema):
        assert isinstance(
            schema, Mapping
        ), "{}.length must be an instance of Mapping".format(self.__class__.__name__)

        super().__init__()
        self.schema = schema

    def _recursive_validate_schema(self, data, field_name, instance):
        for key, v in self.schema.items():
            item = data.get(key) if data else None

            if isinstance(v, self.__class__):  # is another Exodia
                self(key, item, instance)
            else:  # is a Field object
                v._run_validators(item, "{}.".format(field_name) + key, instance)

    def __call__(self, value, field_name=None, instance=None):
        self._recursive_validate_schema(value, field_name, instance)


class Function(Validator):
    def __init__(self, f, message):
        self.f = f
        self.message = message
        super().__init__()

    def get_message(self, field_name):
        return self.message

    def validate(self, value, field_name=None, instance=None):
        return self.f(value)


class Stack(Validator):
    def __init__(self, validators: List[Validator]):
        for i, validator in enumerate(validators):
            assert isinstance(
                validator, Validator
            ), "validators[{}] is not ex.validators.Validator instance".format(str(i))

        self.validators = validators
        self.validator_names = list(map(lambda v: v.__class__.__name__, validators))

    def validate(self, value, field_name=None, instance=None):
        for validator in self.validators:
            try:
                validator(value, field_name, instance)
            except ExodiaException:
                return False

        return True


class Ref(Validator):
    def __init__(self, field, expr, message=None):
        assert isinstance(expr, Callable), "Ref.expr must be a callable"

        self.message = message or "ref expression for {} returned False".format(field)
        self.field = field
        self.expr = expr

        super().__init__()

    def get_message(self, field_name):
        return self.message

    def validate(self, value, field_name=None, instance=None):
        if instance is None:
            raise ExodiaException("can't use Field.ref without an instance context")

        if isinstance(self.field, str):
            field_name = self.field
        else:
            field_name = self.field._name

        if not hasattr(instance, field_name):
            raise ExodiaException(
                "{class_name}.{field} does not exist".format(
                    class_name=instance.__class__.__name__,
                    field=self.field,
                )
            )

        # no __dict__ because validation is still running
        return self.expr(value, instance.__dict__[field_name])
