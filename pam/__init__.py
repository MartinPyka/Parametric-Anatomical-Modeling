"""Parametrical Anatomical Mapping for Blender"""

import logging

import bpy

from . import gui
from . import utils
from . import tools
from . import mapping

logger = logging.getLogger(__name__)

bl_info = {
    "name": "PAM",
    "author": "Sebastian Klatt, Martin Pyka",
    "version": (0, 2, 0),
    "blender": (2, 7, 0),
    "license": "GPL v2",
    "description": "Parametric Anatomical Modeling is a method to translate "
                   "large-scale anatomical data into spiking neural networks.",
    "category": "Object"
}

__author__ = bl_info['author']
__license__ = bl_info['license']
__version__ = ".".join([str(s) for s in bl_info['version']])


class PAMPreferencesPane(bpy.types.AddonPreferences):
    """Preferences pane displaying all addon-wide properties.

    Located in
    `File > User Preferences > Addons > Object: PAM"
    """

    bl_idname = __package__
    log_level_items = [
        ("DEBUG", "(4) DEBUG", "", 4),
        ("INFO", "(3) INFO", "", 3),
        ("WARNING", "(2) WARNING", "", 2),
        ("ERROR", "(1) ERROR", "", 1),
    ]
    data_location = bpy.utils.user_resource(
        "DATAFILES",
        path=__package__,
        create=True
    )
    log_directory = bpy.props.StringProperty(
        name="Log Directory",
        default=data_location,
        subtype="DIR_PATH",
        update=utils.log.callback_properties_changed
    )
    log_filename = bpy.props.StringProperty(
        name="Log Filename",
        default="pam.log",
        update=utils.log.callback_properties_changed
    )
    log_level = bpy.props.EnumProperty(
        name="Log Level",
        default="ERROR",
        items=log_level_items,
        update=utils.log.callback_properties_changed
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Logging:")
        col.prop(self, "log_directory", text="Directory")
        col.prop(self, "log_filename", text="Filename")
        col.prop(self, "log_level", text="Level")


def register():
    """Called on enabling this addon"""
    bpy.utils.register_class(PAMPreferencesPane)
    utils.log.initialize()

    tools.measure.register()
    tools.visual.register()
    mapping.register()
    gui.menus.register()

    bpy.utils.register_module(__name__)
    logger.debug("Registering addon")


def unregister():
    """Called on disabling this addon"""
    tools.measure.unregister()
    tools.visual.unregister()
    mapping.unregister()
    gui.menus.unregister()

    bpy.utils.unregister_module(__name__)
    logger.debug("Unregistering addon")


if __name__ == "__main__":
    register()
