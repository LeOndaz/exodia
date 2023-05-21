from typing import Mapping

from exodia import ExodiaException


class Validator:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, field_name, value, instance):
        raise NotImplementedError

    def __eq__(self, v):
        return isinstance(v, self.__class__)


class Required(Validator):
    def __call__(self, field_name, value, instance):
        if value is None:
            raise ExodiaException("field {field_name} is required.".format(field_name=field_name))


class Optional(Validator):
    def __call__(self, field_name, value, instance):
        pass


class Length(Validator):
    def __init__(self, length=None):
        self.length = length
        super().__init__()

    def __eq__(self, v):
        return object.__eq__(self, v) and v.length == self.length

    def __call__(self, field_name, value, instance):
        if self.length and len(value) != self.length:
            raise ExodiaException("{field_name} must be of length {length}".format(
                field_name=field_name,
                length=self.length,
            ))


class NotEmpty(Validator):
    def __call__(self, field_name, value, instance):
        if len(value) == 0:
            raise ExodiaException("field {field_name} can't be empty".format(
                field_name=field_name
            ))


class Between(Validator):
    def __init__(self, min: int, max: int):
        super().__init__()
        self.min = min
        self.max = max

    def __call__(self, field_name, value, instance):
        if not self.min <= value <= self.max:
            raise ExodiaException("value of {field_name} must be between {min} and {max}".format(
                field_name=field_name,
                min=self.min,
                max=self.max,
            ))


class Type(Validator):
    def __init__(self, t):
        super().__init__()
        self.t = t

    def __call__(self, field_name, value, instance):
        if value and not isinstance(value, self.t):
            raise ExodiaException("{field_name} must be of type {type}".format(
                field_name=field_name,
                type=self.t.__name__,
            ))


class MultipleOf(Validator):
    def __init__(self, n):
        super().__init__()
        self.n = n

    def __call__(self, field_name, value, instance):
        if not value % self.n == 0:
            raise ExodiaException("{field_name}={value} is not a multiple of {n}".format(
                field_name=field_name,
                value=value,
                n=self.n
            ))

    def __eq__(self, v):
        return isinstance(v, self.__class__) and self.n == v.n


class Enum(Validator):
    def __init__(self, options):
        self.options = options
        super().__init__()

    def __call__(self, field_name, value, instance):
        if value not in self.options:
            raise ExodiaException("{field_name}={value} is not in allowed enum choices [{c}]".format(
                field_name=field_name,
                value=value,
                c=" ,".join([str(item) for item in self.options]),
            ))


class MinLength(Validator):
    def __init__(self, length):
        super().__init__()
        self.length = length

    def __call__(self, field_name, value, instance):
        if len(value) < self.length:
            raise ExodiaException("{class_name}{field_name}={value} must have length greater than {l}".format(
                class_name=instance.__class__.__name__,
                field_name=field_name,
                value=value,
                l=self.length,
            ))


class MaxLength(Validator):
    def __init__(self, length):
        super().__init__()
        self.length = length

    def __call__(self, field_name, value, instance):
        if len(value) > self.length:
            raise ExodiaException("{class_name}{field_name}={value} must have length less than {l}".format(
                class_name=instance.__class__.__name__,
                field_name=field_name,
                value=value,
                l=self.length,
            ))


class MinValue(Validator):
    def __init__(self, v):
        super().__init__()
        self.v = v

    def __call__(self, field_name, value, instance):
        if value < self.v:
            raise ExodiaException("{class_name}{field_name}={value} must have length greater than {v}".format(
                class_name=instance.__class__.__name__,
                field_name=field_name,
                value=value,
                v=self.v,
            ))


class MaxValue(Validator):
    def __init__(self, v):
        super().__init__()
        self.v = v

    def __call__(self, field_name, value, instance):
        if value > self.v:
            raise ExodiaException("{class_name}{field_name}={value} must have length less than {v}".format(
                class_name=instance.__class__.__name__,
                field_name=field_name,
                value=value,
                v=self.v,
            ))


class Exodia(Validator):
    def __init__(self, schema):
        super().__init__()
        self.schema = schema

    def recursive_validate_schema(self, field_name, data, instance):
        for key, v in self.schema.items():
            item = data.get(key) if data else None

            if isinstance(v, self.__class__):
                self(key, item, instance)
            else:
                v.run_validators("{}.".format(field_name) + key, item, instance)

    def __call__(self, field_name, data, instance):
        self.recursive_validate_schema(field_name, data, instance)
