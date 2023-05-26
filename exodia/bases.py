import exodia as ex

__all__ = ("Base",)


class Base:
    """
    Basic implementation of a class that saves each kwarg on its instances
    """

    def __init__(self, **kwargs):
        self._validate_kwargs(kwargs)

    def _get_valid_fields(self):
        result = {}

        for key, value in self.__class__.__dict__.items():
            if isinstance(value, ex.Field):
                result[key] = value

        return result

    def _validate_kwargs(self, kwargs):
        errors = []

        unknown_attrs = []
        valid_fields = self._get_valid_fields()
        valid_attrs = {key: kwargs.get(key) for key in valid_fields.keys()}

        for key, value in kwargs.items():
            if not valid_fields.get(key):
                unknown_attrs.append(key)

        for attr in unknown_attrs:
            error = ex.ExodiaException("unexpected attribute {attr}".format(attr=attr))
            errors.append(error)

        for key, field in valid_fields.items():
            value = valid_attrs.get(key)

            try:
                self.validate_field(field, key, value)
            except ex.ExodiaException as e:
                errors += [e]

            setattr(self, key, value)

        try:
            self.validate(valid_attrs)
        except AssertionError as e:
            errors.append(ex.ExodiaException(*e.args))
        except ex.ExodiaException as e:
            errors.append(e)

        if errors:
            raise ex.ExodiaException(errors)

    def validate_field(self, field, field_name, value):
        """
        This is the initial Field validation, runs before validate, during the validation process.
        :param field: An ex.Field instance
        :param field_name: A string with the field name
        :param value: The value to validate
        :return: None
        :raises: ex.ExodiaException
        """
        field._run_validators(value, field_name, self)

    def validate(self, attrs):
        """
        Override to do custom validation, runs after the validation happens
        :param attrs: Mapping of attributes to validate
        :return: None
        """
