from exodia.utils import get_field_attrs


class Base:
    def _validate_kwargs(self, kwargs):
        field_attrs = get_field_attrs(self.__class__.__dict__)

        for key, value in field_attrs.items():
            value.run_validators(key, kwargs.get(key), self)

    def __init__(self, **kwargs):
        self._validate_kwargs(kwargs)
