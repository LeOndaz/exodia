### EXODIA validation

This library is heavily inspired by [Yup](https://github.com/jquense/yup) & [Joi](https://joi.dev/api/?v=17.9.1) in
JavaScript.

## Installation

```shell
pip install exodia
```

## Examples

```python
import exodia as ex


class Person:
    first_name = ex.String().required().max(250)
    last_name = ex.String().required().max(250)
    age = ex.Integer().required().min(18)


child = Person()
child.first_name = None  # throws exception
child.first_name = 12  # throws exception

child.first_name = "".join([i for i in range(250 + 1)])  # exception

child.age = 12  # error, must be more than 18!
```

Not just that, wait to see the Exodia!

![exodia image](https://www.gundamplanet.com/media/catalog/product/cache/9d7675fe917d5a3f85f638a0d3dd8fd7/f/r/frs-a_exodia_gp_en.jpg)

```python
import exodia as ex


class Person:
    children = ex.Exodia({
        'name': ex.String().required(),
        'age': ex.Integer().optional(),
        'children': ex.Exodia({
            ...
        })
    })
```

As you can see, you can stack Exodias to increase your attack!

```python
import exodia as ex


class Person:
    some_number = ex.Integer().between(100, 250)
    some_choice = ex.String().enum(['Choice 1', 'Choice 2'])
```

Or, you can validate an instance (as you'll usually need)

```python
import exodia as ex


class Person(ex.Base):
    name = ex.String().required()
    age = ex.Integer().required().min(18)


me = Person(name="name", age=12)  # validation will work, throws exception
```

### Or, inline validation

```python
import exodia as ex


@router.post('/cards')
def handle_card_creation(request, body):
    order_by = body.order_by  # can be any string

    try:
        ex.String().enum(['ASC', 'DESC']).validate(order_by)
    except ex.ExodiaException:
        raise BigAPIError('invalid order_by value!')

```

### Notice that, if you validate like this

```python
import exodia as ex


class Person(ex.Base):
    name = ex.String()


Person().name = 2  # name=2 is of type int, expected type str
```

However, if you validate without a field name:

```python
import exodia as ex

ex.String().validate(2)  # 2 is of type int, expected type str
```

You'll notice that the error changed, that's because of how descriptors work and all fields in the library are
descriptors.

Custom validation? Just subclass `ex.Validator` and you're good to go.

```python
import exodia as ex


class MultipleOf5And25(ex.Validator):
    def validate(self, value, field_name=None, instance=None):
        """Returns a valid case"""
        return value % 5 == 0 and value % 25 == 0


MultipleOf5And25().validate(20)  # error
MultipleOf5And25().validate(25)  # works

```

What about a custom field?

```python
from collections.abc import Callable
import exodia as ex


class Func(ex.Field):
    of_type = Callable


class Person:
    get_full_name = Func().required()
```

And you're good to go, as expected!

### What if I want only the validation

```python
from collections.abc import Callable
from exodia import validators

multiple_of_25 = validators.MultipleOf(25)
multiple_of_25(30)  # error

is_int = validators.Type(int)
is_int("CLEARLY_NOT_INT")  # error

is_callable = validators.Type(Callable)
is_callable(is_int)  # works
```

__Note__ that there's already a `callable` function in python.

You could even implement a stack of validators!

```python
import exodia as ex


class ValidatorStack(ex.Validator):
    def __init__(self, validators):
        self.validators = validators

    def validate(self, value, field_name=None, instance=None):
        for validator in self.validators:
            try:
                validator.validate(value, field_name, instance)
            except ex.ExodiaException:
                return False

        return True
```

And use it!

```python
validate_multiple_of_5_and_25 = ValidatorStack(validators=[
    ex.validators.MultipleOf(5),
    ex.validators.MultipleOf(25),
])

validate_multiple_of_5_and_25(30)  # everything explodes
```

However, we do have this included as `ex.Stack`

Exodia supports date/time/datetime objects as well with operators working as expected

```python
from datetime import datetime, date
import exodia as ex

ex.Date().before(date(year=3000, month=1, day=1)).validate(date(year=1971, month=1, day=1).isoformat())  # works
ex.DateTime().validate(datetime(year=1971, month=1, day=1, hour=1, minute=1, second=1).isoformat())  # works
```

### What if you have dependant fields?

```python
import exodia as ex


class Person(ex.Base):
    age = ex.Integer().required()
    younger_brother_age = ex.Integer().required()

    def validate(self, attrs):
        # no need to check if age in attrs, you can't get into this step
        # without providing both because both are required
        # any assertion errors are transformed into ex.ExodiaException instances
        assert attrs['age'] > attrs['younger_brother_age'], "PUT IN YOUR MESSAGE"
```

However, that's not the only way to do it

```python
import exodia as ex


class Person(ex.Base):
    age = ex.Integer().required()
    younger_brother_age = (
        ex.Integer()
            .ref(
            age,
            lambda me, my_bro: my_bro > me, "younger brother can't be older!"
        )
    )
```

### OR

```python
import exodia as ex


class Person(ex.Base):
    younger_brother_age = (
        ex.Integer()
            .ref(
            'age',
            lambda me, my_bro: my_bro > me, "younger brother can't be older!"
        )
    )
    age = ex.Integer().required()
```

Notice the quotes, we need to respect python lexing order, `age` is defined after `younger_brother_age`,
so we can't reference it


More is coming, actually more is still undocumented!
