from exodia.utils import get_field_attrs


class Base:
    """
    Basic implementation of a class that saves each kwarg on its instances
    """
    def _validate_kwargs(self, kwargs):
        field_attrs = get_field_attrs(self.__class__.__dict__)

        for key, value in field_attrs.items():
            value.run_validators(key, kwargs.get(key), self)

    def _set_instance_variables(self, kwargs):
        for key, value in kwargs:
            setattr(self, key, value)

    def __init__(self, **kwargs):
        self._validate_kwargs(kwargs)
        self._set_instance_variables(kwargs)
