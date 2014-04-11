"""Visualization Module"""

import logging
import math

import bpy

from . import colorscheme

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
        context.scene
        return {'FINISHED'}


# TODO(SK): missing docstring
class PamVisualizeKernelReset(bpy.types.Operator):
    bl_idname = "pam.visualize_kernel_reset"
    bl_label = "Reset object"
    bl_description = "Reset object visualization"
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}


# TODO(SK): missing docstring
class PamVisualizeKernelAddCustomParam(bpy.types.Operator):
    bl_idname = "pam.add_param"
    bl_label = "Add param"
    bl_description = "Add custom parameter"
    bl_options = {'UNDO'}

    def execute(self, context):
        prop = context.scene.pam_visualize.customs.add()

        return {'FINISHED'}


# TODO(SK): missing docstring
class PamVisualizeKernelRemoveCustomParam(bpy.types.Operator):
    bl_idname = "pam.remove_param"
    bl_label = "Remove param"
    bl_description = "Remove custom parameter"
    bl_options = {'UNDO'}

    def execute(self, context):
        active_index = context.scene.pam_visualize.active_index
        context.scene.pam_visualize.customs.remove(active_index)

        return {'FINISHED'}


# TODO(SK): missing docstring
def toggle_mode(self, context):
    textured_solid = False
    if self.view_mode == "MAPPED":
        textured_solid = True

    context.space_data.show_textured_solid = textured_solid


# TODO(SK): missing docstring
class PamVisualizeKernelFloatProperties(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
        name="Param name",
        default="param"
    )
    value = bpy.props.FloatProperty(
        name="Float value",
        default=0.0
    )


# TODO(SK): missing docstring
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
    resolution = bpy.props.IntProperty(
        name="Kernel image resolution",
        default=1024,
        min=32,
        max=10240,
        subtype="PIXEL"
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


# TODO(SK): missing docstring
def kernel_image(image, func, u, v, *args):
    width, height = image.size
    x_res = 1.0 / width
    y_res = 1.0 / height

    rgba = (1, 1, 1, 1)

    values = []

    for x in range(width):
        for y in range(height):
            x_in_uv = x * x_res
            y_in_uv = y * y_res

            value = func(x_in_uv, y_in_uv, u, v, *args)
            values.append(value)

    value_min = min(values)
    value_max = max(values)

    logger.debug("min: %f", value_min)
    logger.debug("max: %f", value_max)

    shift_upper = value_max - value_min
    shift_factor = 255.0 / shift_upper

    logger.debug("shift upper: %f", shift_upper)
    logger.debug("shift factor: %f", shift_factor)

    for x in range(width):
        for y in range(height):
            index_image = (x + y * width) * 4
            index_values = x * y

            value = values[index_values]
            # index_color = math.floor((value - value_min) * shift_factor)
            # color = colorscheme.schemes["classic"][index_color]

            for i in range(3):
                image.pixels[index_image + i] = value


# TODO(SK): duplicate
# TODO(SK): missing docstring
def pixel(image, x, y, rgba):
    width, height = image.size
    index = (x + y * width) * 4

    for i in range(4):
        logger.debug("[%i,%i] index: %i", x, y, index)
        image.pixels[index + i] = rgba[i]

    return image


# TODO(SK): missing docstring
def register():
    bpy.utils.register_class(PamVisualizeKernelFloatProperties)
    bpy.utils.register_class(PamVisualizeKernelProperties)
    bpy.types.Scene.pam_visualize = bpy.props.PointerProperty(
        type=PamVisualizeKernelProperties
    )


# TODO(SK): missing docstring
def unregister():
    del bpy.types.Scene.pam_visualize
