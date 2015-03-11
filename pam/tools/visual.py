"""Visualization Module"""

import inspect
import logging
import math

import bpy
import numpy as np

from .. import kernel
from .. import model
from .. import pam
from .. import pam_vis
from ..utils import colors
from ..utils import p

logger = logging.getLogger(__package__)

COLOR = colors.schemes["classic"]


VIEW_LIST = [
    ("NORMAL", "Multitextured", "", 0),
    ("MAPPED", "GLSL", "", 1)
]

MODE_LIST = [
    ("CURSOR", "At cursor", "", 0),
    ("COORDINATES", "At uv", "", 1)
]


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
        pam_visualize = context.scene.pam_visualize

        if active_obj is None:
            return False
        if active_obj.type != "MESH":
            return False
        if pam_visualize.kernel == "NONE":
            return False

        return True

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
                cursor
            )

            logger.debug(
                "object (%s) uvscaling (%f) cursor (%f, %f, %f) uvmapped (%f, %f)",
                active_obj.name,
                uv_scaling_factor,
                cursor[0],
                cursor[1],
                cursor[2],
                u,
                v
            )
        elif pam_visualize.mode == "COORDINATES":
            u = pam_visualize.u
            v = pam_visualize.v

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
        # temp_material.use_shadeless = True

        kwargs = {p.name: p.value / uv_scaling_factor for p in pam_visualize.customs}

        kernel_func = next(getattr(kernel, k) for (k, n, d, n) in kernel.KERNEL_TYPES if k == pam_visualize.kernel)

        kernel_image(
            np.array([u, v]),
            temp_image,
            kernel_func,
            kwargs
        )

        temp_texture.image = temp_image

        tex_slot = temp_material.texture_slots.add()
        tex_slot.texture = temp_texture
        tex_slot.texture_coords = "UV"
        tex_slot.mapping = "FLAT"
        # tex_slot.use_map_color_diffuse = True

        temp_material.diffuse_intensity = 1.0
        temp_material.specular_intensity = 0.0

        active_obj.data.materials.clear(update_data=True)
        active_obj.data.materials.append(temp_material)

        context.scene.update()

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

    @classmethod
    def poll(cls, context):
        pam_visualize = context.scene.pam_visualize

        if pam_visualize.kernel == "NONE":
            return False

        return True

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
        active_o = bpy.context.active_object
        pam_vis.visualizeClean()
        if active_o:
                active_o.select = True
        bpy.context.scene.objects.active = active_o

        return {'FINISHED'}


class PamVisualizeAllConnections(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_connections_all"
    bl_label = "Visualize All Connections"
    bl_description = "Visualizes all outgoing connections"
    bl_options = {'UNDO'}

    def execute(self, context):
        connections = context.scene.pam_visualize.connections
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
        print('Neuron Number: ' + str(p_index))

        smoothing = context.scene.pam_visualize.smoothing
        for ci in model.CONNECTION_INDICES:
            # if ng_index is the pre-synaptic layer in a certain mapping
            if ci[1] == ng_index:
                # visualize the connections
                pam_vis.visualizeConnectionsForNeuron(ci[0], p_index, smoothing)

        bpy.context.scene.objects.active = object
        return {'FINISHED'}


class PamVisualizeForwardConnection(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_forward_connection"
    bl_label = "Visualize Forward Connection for Neuron at Cursor"
    bl_description = "Visualizes as many mappings as possible until the synaptic layer"
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
        print('Neuron Number: ' + str(p_index))

        for ci in model.CONNECTION_INDICES:
            # if ng_index is the pre-synaptic layer in a certain mapping
            if ci[1] == ng_index:
                # visualize the connections
                pam_vis.visualizeForwardMapping(ci[0], p_index)

        bpy.context.scene.objects.active = object
        return {'FINISHED'}


# TODO(SK): missing docstring
@p.profiling
def kernel_image(guv, image, func, kwargs):
    width, height = image.size
    if width != height:
        pass

    res = 1.0 / width

    ranges = list(map(lambda x: x * res, range(width)))

    values = [func(np.array([u, v]), guv, **kwargs) for v in ranges for u in ranges]
    color_index = list(map(lambda x: math.floor(x * 255.0), values))

    color_values = [COLOR[i] for i in color_index]

    image.pixels = [value for color in color_values for value in color]


def get_kernels(self, context):
    return kernel.KERNEL_TYPES


def update_kernels(self, context):
    self.customs.clear()
    func = next(getattr(kernel, k) for (k, n, d, n) in kernel.KERNEL_TYPES if k == self.kernel)
    if func is not None:
        args, _, _, defaults = inspect.getargspec(func)
        if args and defaults:
            args = args[-len(defaults):]
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
    viewport_shade = "SOLID"

    if self.view == "MAPPED":
        textured_solid = True
        material_mode = "GLSL"
        viewport_shade = "TEXTURED"

    context.space_data.show_textured_solid = textured_solid
    context.scene.game_settings.material_mode = material_mode
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.viewport_shade = viewport_shade


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
        name="View mode",
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
    connections = bpy.props.IntProperty(
        name="Number of Connections per Mapping",
        default=3,
        min=1,
        max=20
    )

    smoothing = bpy.props.IntProperty(
        name="Number of smoothing steps",
        default=5,
        min=0,
        max=20
    )

    active_index = bpy.props.IntProperty()
    customs = bpy.props.CollectionProperty(
        type=PamVisualizeKernelFloatProperties
    )
    u = bpy.props.FloatProperty()
    v = bpy.props.FloatProperty()
