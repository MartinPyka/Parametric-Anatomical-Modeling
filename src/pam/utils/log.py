"""Log Module"""

import logging
import os

import bpy

# TODO(SK): root module solution flaky
ROOT_MODULE = "pam"


def filepath():
    """Returns root log filepath"""

    prefs = bpy.context.user_preferences.addons[ROOT_MODULE].preferences
    return prefs.log_directory


def filename():
    """Returns log filename"""

    prefs = bpy.context.user_preferences.addons[ROOT_MODULE].preferences
    return prefs.log_filename


def fullpath():
    """Returns complete path to logfile"""

    return "%s/%s" % (filepath(), filename())


def level():
    """Returns log level"""

    prefs = bpy.context.user_preferences.addons[ROOT_MODULE].preferences
    return getattr(logging, prefs.log_level)


def initialize():
    """Registering log handlers"""

    if not os.path.exists(filepath()):
        default_location = bpy.utils.user_resource(
            "DATAFILES",
            path=ROOT_MODULE,
            create=True
        )
        prefs = bpy.context.user_preferences.addons[ROOT_MODULE].preferences
        prefs.log_directory = default_location

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s  %(message)s  "
        "[%(filename)s:%(lineno)s]",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Setting up loghandlers for stdout and file logging
    streamhandler = logging.StreamHandler()
    filehandler = logging.FileHandler(
        filename=(fullpath()),
        mode="a",
        encoding="utf-8"
    )

    streamhandler.setFormatter(formatter)
    filehandler.setFormatter(formatter)

    logger = logging.getLogger(ROOT_MODULE)
    logger.setLevel(level())
    logger.addHandler(streamhandler)
    logger.addHandler(filehandler)


def callback_properties_changed(self, context):
    """A Callback for addapt to changed logging properties.

    Should be called whenever a logging property (filepath, level, filename)
    is changed.
    """

    logger = logging.getLogger(ROOT_MODULE)
    logger.handlers = []
    initialize()
