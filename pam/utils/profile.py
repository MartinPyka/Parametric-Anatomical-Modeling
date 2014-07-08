"""Profile Module"""

import logging
import timeit

logger = logging.getLogger(__package__)


def profiling(func):
    """Profiling functions in miliseconds"""
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        duration = (timeit.default_timer() - start_time) * 1000
        logger.debug("%s in %d ms", func.__name__, duration)
        return result
    return wrapper
