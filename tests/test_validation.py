import pytest

from exodia import ExodiaException


def test_put_invalid_choice(instance):
    with pytest.raises(ExodiaException):
        instance.size = 'MEDIUM'


def test_put_valid_choice(instance):
    instance.choices = 'BIG'
    instance.choices = 'SMALL'


def test_optional_field(instance):
    instance.last_name = None


def test_required_field(instance):
    with pytest.raises(ExodiaException):
        instance.first_name = None


def test_put_invalid_type(instance):
    with pytest.raises(ExodiaException):
        instance.first_name = 1


def test_put_dict_with_all_keys(instance):
    instance.obj = {
        "name": "LeOndaz",
        "age": 23
    }


def test_put_dict_with_missing_required_key(instance):
    with pytest.raises(ExodiaException):
        instance.obj = {
            "age": 23
        }


def test_put_dict_with_missing_optional_key(instance):
    instance.obj = {
        "name": "LeOndaz"
    }


def test_nested_object(instance):
    instance.nested_obj = {
        "nested": {
            "random": "yes",
            "age": 23
        }
    }
