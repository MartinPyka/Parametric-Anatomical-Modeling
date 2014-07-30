"""Profile Module"""

import logging
import cProfile as pf

logger = logging.getLogger(__package__)


def profiling(func):
    """Profiling functions in miliseconds"""
    def wrapper(*args, **kwargs):
        profiler = pf.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        profiler.print_stats()
        return result
    return wrapper
