import pytest

import exodia as ex


class TestClass:
    first_name = ex.String().required()
    last_name = ex.String().optional()
    size = ex.String().required().enum(['BIG', 'SMALL'])
    obj = ex.Exodia({
        'name': ex.String().required(),
        'age': ex.Integer().optional(),
    }).required()
    nested_obj = ex.Exodia({
        'nested': ex.Exodia({
            'random': ex.String().required(),
            'age': ex.Integer().required(),
        })
    })


@pytest.fixture()
def instance():
    test_class = TestClass()

    return test_class
