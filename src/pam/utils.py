"""Utils Module"""

import logging
import timeit

import bpy

logger = logging.getLogger(__package__)


def log_filepath():
    """Returns root log filepath"""

    prefs = bpy.context.user_preferences.addons[__package__].preferences
    return "%s/%s" % (prefs.log_directory, prefs.log_filename)


def log_level():
    """Returns log level"""

    prefs = bpy.context.user_preferences.addons[__package__].preferences
    return getattr(logging, prefs.log_level)


def log_initialize():
    """Registering log handlers"""

    filepath = log_filepath()
    level = log_level()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] "
            "[%(module)s:%(funcName)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d, %H:%M:%S"
    )

    # Setting up loghandlers for stdout and file logging
    streamhandler = logging.StreamHandler()
    filehandler = logging.FileHandler(
        filename=filepath,
        mode="a",
        encoding="utf-8"
    )

    streamhandler.setFormatter(formatter)
    filehandler.setFormatter(formatter)

    logger = logging.getLogger(__package__)
    logger.setLevel(level)
    logger.addHandler(streamhandler)
    logger.addHandler(filehandler)


def log_callback_properties_changed(self, context):
    """A Callback for addapt to changed logging properties.

    Should be called whenever a logging property (filepath, level, filename)
    is changed.
    """

    logger = logging.getLogger(__package__)
    logger.handlers = []
    log_initialize()


def profiling(func):
    """Profiling functions in miliseconds"""
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        duration = (timeit.default_timer() - start_time) * 1000
        logger.debug("%s in %d ms", func.__name__, duration)
        return result
    return wrapper
