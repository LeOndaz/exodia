import pytest

import exodia as ex


def test_put_invalid_choice(instance):
    with pytest.raises(ex.ExodiaException):
        instance.size = "MEDIUM"


def test_put_valid_choice(instance):
    instance.choices = "BIG"
    instance.choices = "SMALL"


def test_optional_field(instance):
    instance.last_name = None


def test_optional_invalid_value(instance):
    with pytest.raises(ex.ExodiaException):
        instance.last_name = 2


def test_required_field(instance):
    with pytest.raises(ex.ExodiaException):
        instance.first_name = None


def test_put_invalid_type(instance):
    with pytest.raises(ex.ExodiaException):
        instance.first_name = 1


def test_put_dict_with_all_keys(instance):
    instance.obj = {"name": "LeOndaz", "age": 23}


def test_put_dict_with_missing_required_key(instance):
    with pytest.raises(ex.ExodiaException):
        instance.obj = {"age": 23}


def test_put_dict_with_missing_optional_key(instance):
    instance.obj = {"name": "LeOndaz"}


def test_nested_object(instance):
    instance.nested_obj = {"nested": {"random": "yes", "age": 23}}


def test_imperative_validation():
    with pytest.raises(ex.ExodiaException):
        ex.String().required().validate(None)

    with pytest.raises(ex.ExodiaException):
        ex.String().min(250).validate("STRING_LESS_THAN_250_CHARS")


def test_custom_validation():
    with pytest.raises(ex.ExodiaException):
        ex.String().function(lambda v: len(v) >= 2, "value has len smaller than 2").validate("A")

    # which is equivalent to

    with pytest.raises(ex.ExodiaException):
        ex.String().min(2).validate('A')
