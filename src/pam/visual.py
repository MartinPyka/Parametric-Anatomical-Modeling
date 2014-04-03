"""Visualization Module"""

import logging

import bpy

logger = logging.getLogger(__package__)


VIEW_LIST = [
    ("NORMAL", "Normal", "", 1),
    ("MAPPED", "Mapped", "", 2)
]

KERNEL_LIST = [
    ("GAUSSIAN", "Gaussian", "", 1),
    ("UNI", "Uni", "", 2)
]


# TODO(SK): missing docstring
class PAMVisualizeKernel(bpy.types.Operator):
    bl_idname = "pam.visualize_kernel"
    bl_label = "Visualize kernel"
    bl_description = "Visualize kernel function on object"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        if active_obj is not None:
            return active_obj.type == "MESH"
        else:
            return False

    def execute(self, context):
        return {'FINISHED'}


class PamVisualizeKernelReset(bpy.types.Operator):
    bl_idname = "pam.visualize_kernel_reset"
    bl_label = "Reset object"
    bl_description = "Reset object visualization"
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}


class PamVisualizeKernelAddCustomParam(bpy.types.Operator):
    bl_idname = "pam.add_param"
    bl_label = "Add param"
    bl_description = "Add custom parameter"
    bl_options = {'UNDO'}

    def execute(self, context):
        prop = context.scene.pam_visualize.customs.add()

        return {'FINISHED'}


class PamVisualizeKernelRemoveCustomParam(bpy.types.Operator):
    bl_idname = "pam.remove_param"
    bl_label = "Remove param"
    bl_description = "Remove custom parameter"
    bl_options = {'UNDO'}

    def execute(self, context):
        active_index = context.scene.pam_visualize.active_index
        context.scene.pam_visualize.customs.remove(active_index)

        return {'FINISHED'}


def toggle_mode(self, context):
    textured_solid = False
    if self.view_mode == "MAPPED":
        textured_solid = True

    context.space_data.show_textured_solid = textured_solid


class PamVisualizeKernelFloatProperties(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
        name="Param name",
        default="param"
    )
    value = bpy.props.FloatProperty(
        name="Float value",
        default=0.0
    )


class PamVisualizeKernelProperties(bpy.types.PropertyGroup):
    view_mode = bpy.props.EnumProperty(
        name="View mode",
        default="NORMAL",
        items=VIEW_LIST,
        update=toggle_mode
    )
    kernel = bpy.props.EnumProperty(
        name="Kernel function",
        default="GAUSSIAN",
        items=KERNEL_LIST
    )
    u = bpy.props.FloatProperty(
        name="u",
        default=0.0,
        min=0.0,
        max=1.0,
    )
    v = bpy.props.FloatProperty(
        name="v",
        default=0.0,
        min=0.0,
        max=1.0,
    )
    active_index = bpy.props.IntProperty()
    field = bpy.props.PointerProperty(
        type=PamVisualizeKernelFloatProperties
    )
    customs = bpy.props.CollectionProperty(
        type=PamVisualizeKernelFloatProperties
    )


def register():
    bpy.utils.register_class(PamVisualizeKernelFloatProperties)
    bpy.utils.register_class(PamVisualizeKernelProperties)
    bpy.types.Scene.pam_visualize = bpy.props.PointerProperty(
        type=PamVisualizeKernelProperties
    )


def unregister():
    del bpy.types.Scene.pam_visualize
