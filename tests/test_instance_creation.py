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
