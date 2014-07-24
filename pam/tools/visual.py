"""Visualization Module"""

import inspect
import logging
import math

import bpy

from .. import kernel
from .. import model
from .. import pam
from .. import pam_vis
from ..utils import colors

logger = logging.getLogger(__package__)


VIEW_LIST = [
    ("NORMAL", "Multitextured", "", 0),
    ("MAPPED", "GLSL", "", 1)
]

MODE_LIST = [
    ("CURSOR", "At cursor", "", 0),
    ("COORDINATES", "At uv", "", 1)
]

KERNELS = {
    "GAUSSIAN": kernel.gaussian.gauss_vis,
    "UNITY": kernel.gaussian.unity_vis
}


# TODO(SK): rephrase descriptions
# TODO(SK): missing docstring
class PAMVisualizeKernel(bpy.types.Operator):
    bl_idname = "pam.visualize"
    bl_label = "Generate kernel texture"
    bl_description = "Generate kernel texture"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        if active_obj is not None:
            return active_obj.type == "MESH"
        else:
            return False

    def execute(self, context):
        active_obj = context.active_object
        pam_visualize = context.scene.pam_visualize

        if active_obj.data.uv_layers.active is None:
            message = "active object has no active uv layer"

            logger.warn(message)
            self.report({"WARNING"}, message)

            return {'CANCELLED'}

        cursor = context.scene.cursor_location.copy()

        uv_scaling_factor, _ = pam.computeUVScalingFactor(active_obj)

        u, v = None, None

        if pam_visualize.mode == "CURSOR":
            u, v = pam.map3dPointToUV(
                active_obj,
                active_obj,
                cursor_location
            )

            logger.debug(
                "object (%s) uvscaling (%f) cursor (%f, %f, %f) uvmapped (%f, %f)",
                active_obj.name,
                uv_scaling_factor,
                cursor_location[0],
                cursor_location[1],
                cursor_location[2],
                u,
                v
            )
        elif pam_visualize.mode == "COORDINATES":
            u = pam_visualize.customs["u"]
            v = pam_visualize.customs["v"]

            logger.debug(
                "object (%s) uvscaling (%f) uv (%f, %f)",
                active_obj.name,
                uv_scaling_factor,
                u,
                v
            )

        temp_image = bpy.data.images.new(
            name="pam.temp_image",
            width=pam_visualize.resolution,
            height=pam_visualize.resolution,
            alpha=True
        )

        temp_texture = bpy.data.textures.new(
            "temp_texture",
            type="IMAGE"
        )

        temp_material = bpy.data.materials.new("temp_material")

        args = [(p.name, p.value / uv_scaling_factor) for p in pam_visualize.customs]

        kernel_image(
            temp_image,
            kernel.gaussian.gauss_vis,
            *args
        )

        temp_texture.image = temp_image

        tex_slot = temp_material.texture_slots.add()
        tex_slot.texture = temp_texture
        tex_slot.texture_coords = "UV"
        tex_slot.mapping = "FLAT"

        temp_material.diffuse_intensity = 1.0
        temp_material.specular_intensity = 0.0

        active_obj.data.materials.clear(update_data=True)
        active_obj.data.materials.append(temp_material)

        return {'FINISHED'}


# TODO(SK): missing docstring
class PAMVisualizeKernelAtCoordinates(bpy.types.Operator):
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
# TODO(SK): needs implementation
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


class PamVisualizeKernelResetCustomParams(bpy.types.Operator):
    bl_idname = "pam.reset_params"
    bl_label = "Reset kernel parameter"
    bl_description = "Remove kernel parameter"
    bl_options = {'UNDO'}

    def execute(self, context):
        pam_visualize = context.scene.pam_visualize
        update_kernels(pam_visualize, context)

        return {'FINISHED'}


class PamVisualizeClean(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_clean"
    bl_label = "Clean Visualizations"
    bl_description = "Removes all visualizations"
    bl_options = {'UNDO'}

    def execute(self, context):
        pam_vis.visualizeClean()

        return {'FINISHED'}


class PamVisualizeAllConnections(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_connections_all"
    bl_label = "Visualize All Connections"
    bl_description = "Visualizes all outgoing connections"
    bl_options = {'UNDO'}

    def execute(self, context):
        connections = context.scene.pam_visualize_conns.connections
        for j in range(0, model.CONNECTION_COUNTER):
            for i in range(0, connections):
                pam_vis.visualizeConnectionsForNeuron(j, i)

        return {'FINISHED'}


class PamVisualizeUnconnectedNeurons(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_unconnected_neurons"
    bl_label = "Visualize Unconnected Neurons"
    bl_description = "Visualizes neurons with no connection"
    bl_options = {'UNDO'}

    def execute(self, context):
        object = context.active_object

        if object.name in model.NG_DICT:
            ng_index = model.NG_DICT[object.name][object.particle_systems[0].name]
        else:
            return {'FINISHED'}

        for ci in model.CONNECTION_INDICES:
            # if ng_index is the pre-synaptic layer in a certain mapping
            if ci[1] == ng_index:
                # visualize the connections
                pam_vis.visualizeUnconnectedNeurons(ci[0])

        bpy.context.scene.objects.active = object
        object.select = True
        return {'FINISHED'}


class PamVisualizeConnectionsForNeuron(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_connections_for_neuron"
    bl_label = "Visualize Connections at Cursor"
    bl_description = "Visualizes all outgoing connections for a neuron at cursor position"
    bl_options = {'UNDO'}

    def execute(self, context):
        object = context.active_object
        cursor = context.scene.cursor_location

        if object.name in model.NG_DICT:
            ng_index = model.NG_DICT[object.name][object.particle_systems[0].name]
        else:
            return {'FINISHED'}

        ng_index = model.NG_DICT[object.name][object.particle_systems[0].name]
        p_index = pam.map3dPointToParticle(object, 0, cursor)

        for ci in model.CONNECTION_INDICES:
            # if ng_index is the pre-synaptic layer in a certain mapping
            if ci[1] == ng_index:
                # visualize the connections
                pam_vis.visualizeConnectionsForNeuron(ci[0], p_index)

        bpy.context.scene.objects.active = object
        return {'FINISHED'}


# TODO(SK): missing docstring
def kernel_image(image, func, *args):
    width, height = image.size
    x_resolution = 1.0 / width
    y_resolution = 1.0 / height

    for x in range(width):
        for y in range(height):
            x_in_uv = x * x_resolution
            y_in_uv = y * y_resolution

            value = func(x_in_uv, y_in_uv, u, v, *args)

            # logger.debug("u: %f v: %f value: %f", x_in_uv, y_in_uv, value)

            pixel_index = (x + y * width) * 4
            color_index = math.floor(value * 255.0)

            color = colors.schemes["classic"][color_index]

            image.pixels[pixel_index:pixel_index + 3] = color


def get_kernels(self, context):
    return [(k, k, "", i) for i, k in enumerate(KERNELS, 1)]


def update_kernels(self, context):
    self.customs.clear()
    func = KERNELS[self.kernel]
    args, _, _, defaults = inspect.getargspec(func)
    params = zip(args, defaults)
    for k, v in params:
        p = self.customs.add()
        p.name = k
        p.value = v


# TODO(SK): missing docstring
def uv_visualize_texture():
    if "pam.temp_texture" in bpy.data.textures:
        logger.debug("using former temporary texture")

        temp_texture = bpy.data.textures["pam.temp_texture"]

    else:
        logger.debug("creating new temporary texture")

        temp_texture = bpy.data.textures.new(
            name="pam.temp_texture",
            type="IMAGE"
        )

    return temp_texture


# TODO(SK): missing docstring
def toggle_view(self, context):
    textured_solid = False
    material_mode = "MULTITEXTURE"

    if self.view == "MAPPED":
        textured_solid = True
        material_mode = "GLSL"

    context.space_data.show_textured_solid = textured_solid
    context.scene.game_settings.material_mode = material_mode


# TODO(SK): missing docstring
def register():
    bpy.utils.register_class(PamVisualizeConnectionProperties)
    bpy.utils.register_class(PamVisualizeKernelFloatProperties)
    bpy.utils.register_class(PamVisualizeKernelProperties)
    bpy.types.Scene.pam_visualize = bpy.props.PointerProperty(
        type=PamVisualizeKernelProperties
    )
    bpy.types.Scene.pam_visualize_conns = bpy.props.PointerProperty(
        type=PamVisualizeConnectionProperties
    )


# TODO(SK): missing docstring
def unregister():
    del bpy.types.Scene.pam_visualize


class PamVisualizeConnectionProperties(bpy.types.PropertyGroup):
    connections = bpy.props.IntProperty(
        name="Number of Connections per Mapping",
        default=3,
        min=1,
        max=20
    )


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
    view = bpy.props.EnumProperty(
        name="View",
        items=VIEW_LIST,
        update=toggle_view
    )
    mode = bpy.props.EnumProperty(
        name="Mode",
        items=MODE_LIST
    )
    kernel = bpy.props.EnumProperty(
        name="Kernel function",
        items=get_kernels,
        update=update_kernels
    )
    resolution = bpy.props.IntProperty(
        name="Kernel image resolution",
        default=128,
        min=2,
        soft_min=8,
        soft_max=4096,
        subtype="PIXEL"
    )
    active_index = bpy.props.IntProperty()
    customs = bpy.props.CollectionProperty(
        type=PamVisualizeKernelFloatProperties
    )
