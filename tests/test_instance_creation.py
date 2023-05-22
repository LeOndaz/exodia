import pytest
import exodia as ex


def test_same_validation_more_than_once():
    with pytest.raises(ex.ExodiaException):
        class TestClass:
            _ = ex.String().optional().optional()


def test_required_then_optional_should_fail():
    with pytest.raises(ex.ExodiaException):
        class TestClass:
            _ = ex.String().optional().required()


def test_base_without_kwargs():
    class Klass(ex.Base):
        required_string = ex.String().required()

    with pytest.raises(ex.ExodiaException):
        _ = Klass()


def test_base_with_missing_kwargs():
    class Klass(ex.Base):
        required_string = ex.String().required()

    with pytest.raises(ex.ExodiaException):
        _ = Klass(name="LeOndaz")


def test_base_with_correct_kwargs():
    class Klass(ex.Base):
        required_string = ex.String().required()

    _ = Klass(required_string="PASS")


def test_instance_with_incorrect_kwargs():
    class Klass(ex.Base):
        required_string = ex.String().required()

    with pytest.raises(ex.ExodiaException):
        _ = Klass(required_string="LeOndaz", required_integer=1, required_func=2)


def test_instantiate_base():
    with pytest.raises(ex.ExodiaException):
        _ = ex.Base()
