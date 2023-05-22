from typing import Mapping

from exodia import ExodiaException


class Validator:
    field_message = None
    generic_message = None

    def __call__(self, value, field_name=None, instance=None):
        raise NotImplementedError

    def __eq__(self, v):
        return isinstance(v, self.__class__)

    def fail(self, field_name=None, **kwargs):
        if field_name:
            raise ExodiaException(self.field_message.format(field_name=field_name, **kwargs))

        raise ExodiaException(self.generic_message.format(**kwargs))


class Required(Validator):
    field_message = "{field_name} is required"
    generic_message = "got None, but a value is required"

    def __call__(self, value, field_name=None, instance=None):
        if value is None:
            self.fail(field_name)


class Optional(Validator):
    """Does nothing"""

    def __call__(self, value, field_name=None, instance=None):
        pass


class Length(Validator):
    field_message = "{field_name} must be of length {length}"
    generic_message = "Length must be {length}"

    def __init__(self, length=None):
        self.length = length
        super().__init__()

    def __eq__(self, v):
        return object.__eq__(self, v) and v.length == self.length

    def __call__(self, value, field_name=None, instance=None):
        if self.length and len(value) != self.length:
            self.fail(field_name, length=self.length)


class NotEmpty(Validator):
    field_message = "{field_name} must not be empty"
    generic_message = "value can't be empty"

    def __call__(self, value, field_name=None, instance=None):
        if len(value) == 0:
            raise ExodiaException("field {field_name} can't be empty".format(
                field_name=field_name
            ))


class Between(Validator):
    field_message = "{field_name} must be between ({min}, {max})"
    generic_message = "{value} is not between ({min}, {max})"

    def __init__(self, min: int, max: int):
        super().__init__()
        self.min = min
        self.max = max

    def __call__(self, value, field_name=None, instance=None):
        if not self.min <= value <= self.max:
            raise self.fail(
                field_name=field_name,
                min=self.min,
                max=self.max,
            )


class Type(Validator):
    generic_message = "{actual_type} is not of type {expected_type}"
    field_message = "{field_name} is not of type {actual_type}"

    def __init__(self, t):
        super().__init__()
        self.t = t

    def __call__(self, value, field_name=None, instance=None):
        if value and not isinstance(value, self.t):
            self.fail(field_name, actual_type=type(value).__name__, expected_type=self.t.__name__)


class MultipleOf(Validator):
    generic_message = "{value} is not a multiple of {n}"
    field_message = "{field_name}={value} is not a multiple of {n}"

    def __init__(self, n):
        super().__init__()
        self.n = n

    def __call__(self, value, field_name=None, instance=None):
        if not value % self.n == 0:
            self.fail(field_name, value=value, n=self.n)

    def __eq__(self, v):
        return isinstance(v, self.__class__) and self.n == v.n


class Enum(Validator):
    field_message = "{value} is not a valid choice for {field_name}, choices are {choices}"
    generic_message = "{value} is not a valid choice, choices are {choices}"

    def __init__(self, options):
        self.options = options
        super().__init__()

    def __call__(self, value, field_name=None, instance=None):
        if value not in self.options:
            self.fail(
                field_name=field_name,
                value=value,
                choices=" ,".join([str(item) for item in self.options]),
            )


class MinLength(Validator):
    field_message = "{class_name}.{field_name}={value} must have length greater than {l}"
    generic_message = "{value} must have length greater than {l}"

    def __init__(self, length):
        super().__init__()
        self.length = length

    def __call__(self, value, field_name=None, instance=None):
        if len(value) < self.length:
            self.fail(
                class_name=instance.__class__.__name__,
                field_name=field_name,
                value=value,
                l=self.length,
            )


class MaxLength(Validator):
    def __init__(self, length):
        super().__init__()
        self.length = length

    def __call__(self, value, field_name=None, instance=None):
        if len(value) > self.length:
            raise ExodiaException("{class_name}{field_name}={value} must have length less than {l}".format(
                class_name=instance.__class__.__name__,
                field_name=field_name,
                value=value,
                l=self.length,
            ))


class MinValue(Validator):
    field_message = "{class_name}.{field_name}={value} must have length greater than {v}"
    generic_message = "{value} must have length greater than {v}"

    def __init__(self, v):
        super().__init__()
        self.v = v

    def __call__(self, value, field_name=None, instance=None):
        if value < self.v:
            self.fail(
                class_name=instance.__class__.__name__,
                field_name=field_name,
                value=value,
                v=self.v,
            )


class MaxValue(Validator):
    generic_message = "{value} must have length greater than {v}"
    field_message = "{class_name}{field_name}={value} must have length less than {v}"

    def __init__(self, v):
        super().__init__()
        self.v = v

    def __call__(self, value, field_name=None, instance=None):
        if value > self.v:
            self.fail(
                class_name=instance.__class__.__name__,
                field_name=field_name,
                value=value,
                v=self.v,
            )


class Exodia(Validator):
    def __init__(self, schema):
        super().__init__()
        self.schema = schema

    def _recursive_validate_schema(self, data, field_name, instance):
        for key, v in self.schema.items():
            item = data.get(key) if data else None

            if isinstance(v, self.__class__):
                self(key, item, instance)
            else:
                v._run_validators(item, "{}.".format(field_name) + key, instance)

    def __call__(self, value, field_name=None, instance=None):
        self._recursive_validate_schema(value, field_name, instance)
