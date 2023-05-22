import inspect


def get_callable_params(c):
    return list(inspect.signature(c).parameters.keys())
