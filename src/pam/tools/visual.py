"""Visualization Module"""

import logging
import math

import bpy

from . import colorscheme
from .. import kernel

logger = logging.getLogger(__package__)


VIEW_LIST = [
    ("NORMAL", "Normal", "", 1),
    ("MAPPED", "Mapped", "", 2)
]

MODE_LIST = [
    ("CURSOR", "Cursor", "", 1),
    ("COORDINATES", "Coordinates", "", 2)
]

KERNEL_LIST = [
    ("GAUSSIAN", "Gaussian", "", 1),
    ("UNI", "Uni", "", 2)
]


# TODO(SK): rephrase descriptions
# TODO(SK): missing docstring
class PAMVisualizeKernelAtCursor(bpy.types.Operator):
    bl_idname = "pam.visualize_cursor"
    bl_label = "Generate kernel image at cursor position"
    bl_description = "Generate kernel image"

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        return active_obj.type == "MESH"

    def execute(self, context):
        active_obj = context.active_object
        cursor_location = context.scene.cursor_location.copy()

        cursor_on_mesh = active_obj.closest_point_on_mesh(cursor_location)

        logger.debug("%s", cursor_on_mesh)

        return {'FINISHED'}


# TODO(SK): missing docstring
class PAMVisualizeKernelGenerateImage(bpy.types.Operator):
    bl_idname = "pam.generate_image"
    bl_label = "Generate kernel image"
    bl_description = "Generate kernel image"

    # TODO(SK): will always return true
    @classmethod
    def poll(cls, context):
        return True

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.label(text="custom")
        layout.template_preview(context.blend_data.textures.get("pam.temp_texture"))

    def execute(self, context):
        pam_visualize = context.scene.pam_visualize

        temp_texture = uv_visualize_texture(context)

        if temp_texture.image is not None:
            current_image = temp_texture.image

        temp_image = context.blend_data.images.new(
            name="pam.temp_image",
            width=pam_visualize.resolution,
            height=pam_visualize.resolution,
            alpha=True
        )

        u = pam_visualize.u
        v = pam_visualize.v

        args = []
        for custom in pam_visualize.customs:
            args.append(custom.value)

        kernel_image(temp_image, kernel.gauss_2d.gauss_viz, u, v, *args)

        context.blend_data.textures["pam.temp_texture"].image = temp_image

        context.scene.update()

        return {'FINISHED'}


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
def toggle_view_mode(self, context):
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
        update=toggle_view_mode
    )
    operator_mode = bpy.props.EnumProperty(
        name="Operator mode",
        default="CURSOR",
        items=MODE_LIST
    )
    kernel = bpy.props.EnumProperty(
        name="Kernel function",
        default="GAUSSIAN",
        items=KERNEL_LIST
    )
    resolution = bpy.props.IntProperty(
        name="Kernel image resolution",
        default=128,
        min=2,
        soft_min=8,
        soft_max=4096,
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
    customs = bpy.props.CollectionProperty(
        type=PamVisualizeKernelFloatProperties
    )


# TODO(SK): missing docstring
def kernel_image(image, func, u, v, *args):
    width, height = image.size
    x_resolution = 1.0 / width
    y_resolution = 1.0 / height

    for x in range(width):
        for y in range(height):
            x_in_uv = x * x_resolution
            y_in_uv = (height - y) * y_resolution

            value = func(x_in_uv, y_in_uv, u, v, *args)

            logger.debug("x: %f y: %f value: %f", x_in_uv, y_in_uv, value)

            pixel_index = (x + y * width) * 4
            color_index = 255 - math.floor(value * 255.0)

            color = colorscheme.schemes["classic"][color_index]

            image.pixels[pixel_index:pixel_index + 3] = map(lambda x: x / 255.0, color)


# TODO(SK): missing docstring
def uv_visualize_texture(context):
    if "pam.temp_texture" in context.blend_data.textures:
        temp_texture = context.blend_data.textures["pam.temp_texture"]

    else:
        temp_texture = context.blend_data.textures.new(
            name="pam.temp_texture",
            type="IMAGE"
        )

    return temp_texture


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
