
### EXODIA validation

This library is heavily inspired by [Yup](https://github.com/jquense/yup) & [Joi](https://joi.dev/api/?v=17.9.1) in JavaScript.

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

child.age = 12 # error, must be more than 18!
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

me = Person(name="name", age=12) # validation will work, throws exception
```

And more is coming, actually more is still undocumented!