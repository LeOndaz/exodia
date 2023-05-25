import inspect
import logging


def get_callable_params(c):
    return list(inspect.signature(c).parameters.keys())


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
