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


class PAMToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all neuronal modelling operations"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Base"
    bl_category = "PAM"

    def draw(self, context):
        layout = self.layout
        col = layout.column()


class PAMMeasureToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all measurment operations"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Measure"
    bl_category = "PAM"

    def draw(self, context):
        active_obj = context.active_object

        name = mesh_object_name(active_obj)

        layout = self.layout
        layout.label("Active object: %s" % name)

        row = layout.row()
        col = row.column()
        col.prop(context.scene.pam_measure, "quantity", text="Neurons")
        col.prop(context.scene.pam_measure, "area", text="Area")

        row = layout.row()
        col = row.column()
        op = col.operator("pam.measure_layer", "Calculate")
        col.label("Total number of neurons:")
        col.label("%d" % context.scene.pam_measure.neurons)


class PAMVisualizeKernelToolsPanel(bpy.types.Panel):
    """A tools panel for visualization of kernel function """

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Visualize kernel"
    bl_category = "PAM"

    def draw(self, context):
        active_obj = context.active_object

        name = mesh_object_name(active_obj) 
        customs = context.scene.pam_visualize.customs

        layout = self.layout
        layout.label("Active object: %s" % name)

        row = layout.row()
        row.prop(context.scene.pam_visualize, "kernel", text="Kernel")

        row = layout.row()
        col = row.column(align=True)
        col.prop(context.scene.pam_visualize, "name", text="")
        col.prop(context.scene.pam_visualize, "value", text="Value")

        row = layout.row()
        op = row.operator("pam.add_param", "Add parameter")

        row = layout.row()
        row.prop(context.scene.pam_visualize, "customs")

        row = layout.row()
        row.template_list(
            listtype_name="UI_UL_list",
            dataptr=context.scene.pam_visualize,
            propname="customs",
            active_dataptr=context.scene.pam_visualize,
            active_propname="index",
            type="DEFAULT"
        )

        row = layout.row()
        op = row.operator("pam.visualize_kernel", "Visualize")

        row = layout.row()
        op = row.operator("pam.visualize_kernel_reset", "Reset")


class PAMTestPanel(bpy.types.Panel):
    """Test Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Testing"
    bl_category = "PAM"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(
            "pam.test_operator",
        )

# TODO(SK): missing docstring
class CustomPropList(bpy.types.UIList):
    def draw_item(self, context, layout, data item, icon, active_data,
                  active_propname, index):
        pass

def mesh_object_name(obj):
    name = ""
    if obj is not None:
        if obj.type == "MESH":
            name = obj.name

    return name
