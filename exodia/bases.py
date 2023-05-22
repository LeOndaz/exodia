import exodia as ex


class Base:
    """
    Basic implementation of a class that saves each kwarg on its instances
    """

    def __new__(cls, *args, **kwargs):
        if cls == Base:
            raise ex.ExodiaException("Can't instantiate Base directly, You must subclass it")

        return super().__new__(cls)

    def _get_valid_attrs(self):
        result = {}

        for key, value in self.__class__.__dict__.items():
            if isinstance(value, ex.Field):
                result[key] = value

        return result

    def _validate_kwargs(self, kwargs):
        errors = []
        unknown_args = []
        valid_attrs = self._get_valid_attrs()

        for key, value in kwargs.items():
            if not valid_attrs.get(key):
                unknown_args.append(key)

        for arg in unknown_args:
            error = ex.ExodiaException("unexpected argument {arg}".format(arg=arg))
            errors.append(error)

        if errors:
            raise ex.ExodiaException(errors)

        for key, value in valid_attrs.items():
            value._run_validators(kwargs.get(key), key, self)

    def _set_instance_variables(self, kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init__(self, **kwargs):
        self._validate_kwargs(kwargs)
        self._set_instance_variables(kwargs)
