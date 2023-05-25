from datetime import date

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
        ex.String().function(
            lambda v: len(v) >= 2, "value has len smaller than 2"
        ).validate("A")

    # which is equivalent to

    with pytest.raises(ex.ExodiaException):
        ex.String().min(2).validate("A")


def test_date():
    unix_epoch = (
        ex.Date()
        .after(date(year=1900, month=1, day=1))
        .before(date(year=2000, month=1, day=1))
        .optional()
        .validate(date(year=1970, month=1, day=1).isoformat())
    )
    assert unix_epoch == date(year=1970, month=1, day=1), "invalid date in test"


def test_cant_use_ref_without_instance():
    with pytest.raises(ex.ExodiaException):
        ex.String().ref("other", lambda this, other: this > other).validate("TEXT")


def test_ref():
    class Person(ex.Base):
        age = ex.Integer().required()
        younger_brother_age = (
            ex.Integer()
            .ref(
                age,
                lambda younger_age, age: age > younger_age,
                "younger_brother can't be older!",
            )
            .required()
        )

    Person(age=25, younger_brother_age=20)

    with pytest.raises(ex.ExodiaException):
        Person(age=25, younger_brother_age=90)


def test_ref_with_string_field():
    class Person(ex.Base):
        age = ex.Integer().required()
        younger_brother = (
            ex.Integer()
            .ref("age", lambda younger_age, age: age > younger_age)
            .required()
        )

    with pytest.raises(ex.ExodiaException):
        Person(age=25, younger_brother=30)


def test_validate_method():
    class Person(ex.Base):
        age = ex.Integer().required()
        younger_brother_age = ex.Integer().required()

        def validate(self, attrs):
            # no need to check if age in attrs, you can't get into this step
            # without providing both because both are required
            # any assertion errors are transformed into ex.ExodiaException instances
            assert attrs["age"] > attrs["younger_brother_age"]

    with pytest.raises(ex.ExodiaException):
        Person(age=25, younger_brother_age=30)
