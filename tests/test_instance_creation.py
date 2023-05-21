import pytest
import exodia as ex


def test_same_validation_more_than_once():
    with pytest.raises(ex.ExodiaException):
        class TestClass:
            my_number = ex.String().optional().optional()


def test_required_then_optional_should_fail():
    with pytest.raises(ex.ExodiaException):
        class TestClass:
            my_x = ex.String().optional().required()


def test_base_without_kwargs():
    class Klass(ex.Base):
        required_string = ex.String().required()

    with pytest.raises(ex.ExodiaException):
        instance = Klass()


def test_base_with_incorrect_kwargs():
    class Klass(ex.Base):
        required_string = ex.String().required()

    with pytest.raises(ex.ExodiaException):
        instance = Klass(name="LeOndaz")


def test_base_with_correct_kwargs():
    class Klass(ex.Base):
        required_string = ex.String().required()

    instance = Klass(required_string="PASS")
