"""PAM Gui Module"""

import logging

import bpy

from . import utils

logger = logging.getLogger(__package__)


class PAMPreferencesPane(bpy.types.AddonPreferences):
    """Preferences pane displying all addon-wide properties.

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
        update=utils.log_callback_properties_changed
    )
    log_filename = bpy.props.StringProperty(
        name="Log Filename",
        default="pam.log",
        update=utils.log_callback_properties_changed
    )
    log_level = bpy.props.EnumProperty(
        name="Log Level",
        default="ERROR",
        items=log_level_items,
        update=utils.log_callback_properties_changed
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Logging:")
        col.prop(self, "log_directory", text="Directory")
        col.prop(self, "log_filename", text="Filename")
        col.prop(self, "log_level", text="Level")
