"""Mapping module"""

import logging
import inspect
import random

import bpy

from . import kernel
from . import model
from . import pam

logger = logging.getLogger(__package__)


NONE = [
    ("none", "None", "", "", 0),
]

LAYER_TYPES = NONE + [
    ("postsynapse", "Postsynapse", "", "", 1),
    ("postintermediates", "Postintermediate", "", "", 2),
    ("synapse", "Synapse", "", "", 3),
    ("preintermediates", "Preintermediate", "", "", 4),
    ("presynapse", "Presynapse", "", "", 5),
]

MAPPING_TYPES = NONE + [
    ("euclid", "Euclidean", "", "", 1),
    ("normal", "Normal", "", "", 2),
    ("top", "Topology", "", "", 3),
    ("uv", "UV", "", "", 4),
    ("rand", "Random", "", "", 5)
]

MAPPING_DICT = {
    "euclid": pam.MAP_euclid,
    "normal": pam.MAP_normal,
    "rand": pam.MAP_random,
    "top": pam.MAP_top,
    "uv": pam.MAP_uv
}

DISTANCE_TYPES = NONE + [
    ("euclid", "Euclidean", "", "", 1),
    ("euclidUV", "EuclideanUV", "", "", 2),
    ("jumpUV", "jumpUV", "", "", 3),
    ("UVjump", "UVjump", "", "", 4),
    ("normalUV", "NormalUV", "", "", 5),
    ("UVnormal", "UVnormal", "", "", 6),
]

DISTANCE_DICT = {
    "euclid": pam.DIS_euclid,
    "euclidUV": pam.DIS_euclidUV,
    "jumpUV": pam.DIS_jumpUV,
    "UVjump": pam.DIS_UVjump,
    "normalUV": pam.DIS_normalUV,
    "UVnormal": pam.DIS_UVnormal
}

KERNEL_TYPES = NONE + kernel.KERNEL_TYPES


def particle_systems(self, context):
    p = NONE[:]

    if self.object not in context.scene.objects:
        return p

    particles = context.scene.objects[self.object].particle_systems
    if not any(particles):
        return p

    p += [(p.name, p.name, "", "", i) for i, p in enumerate(particles, start=1)]

    return p


def active_mapping_index(self, context):
    m = context.scene.pam_mapping
    active_set = m.sets[m.active_set]

    index = -1

    for i, mapping in enumerate(active_set.mappings):
        if self == mapping:
            index = i
            break

    return index


def uv_source(self, context):
    p = NONE[:]

    m = context.scene.pam_mapping
    active_set = m.sets[m.active_set]

    index = active_mapping_index(self, context)

    if index == -1:
        return p

    layer = active_set.layers[index]

    if layer.object not in context.scene.objects:
        return p

    uv_layers = context.scene.objects[layer.object].data.uv_layers
    if not any(uv_layers):
        return p

    p += [(l.name, l.name, "", "", i) for i, l in enumerate(uv_layers, start=1)]

    return p


def uv_target(self, context):
    p = NONE[:]

    m = context.scene.pam_mapping
    active_set = m.sets[m.active_set]

    index = active_mapping_index(self, context)

    if index == -1:
        return p

    if len(active_set.layers) <= index + 1:
        return p

    layer = active_set.layers[index + 1]

    if layer.object not in context.scene.objects:
        return p

    uv_layers = context.scene.objects[layer.object].data.uv_layers
    if not any(uv_layers):
        return p

    p += [(l.name, l.name, "", "", i) for i, l in enumerate(uv_layers, start=1)]

    return p


def update_object(self, context):
    self.kernel.object = self.object


def update_kernels(self, context):
    self.parameters.clear()
    name = next(f for (f, _, _, _) in kernel.KERNEL_TYPES if f == self.function)
    func = getattr(kernel, name)
    if func is not None:
        args, _, _, defaults = inspect.getargspec(func)
        if args and defaults:
            args = args[-len(defaults):]
            params = zip(args, defaults)
            for k, v in params:
                p = self.parameters.add()
                p.name = k
                p.value = v


class PAMKernelValues(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
        name="Parameter name",
        default="param"
    )
    value = bpy.props.FloatProperty(
        name="Float value",
        default=0.0
    )


class PAMKernelParameter(bpy.types.PropertyGroup):
    object = bpy.props.StringProperty()
    function = bpy.props.EnumProperty(
        name="Kernel function",
        items=KERNEL_TYPES,
        update=update_kernels,
    )
    parameters = bpy.props.CollectionProperty(
        type=PAMKernelValues
    )
    particles = bpy.props.EnumProperty(
        name="Particle system",
        items=particle_systems,
    )
    active_parameter = bpy.props.IntProperty()


class PAMMappingParameter(bpy.types.PropertyGroup):
    function = bpy.props.EnumProperty(
        name="Mapping function",
        items=MAPPING_TYPES,
    )
    distance = bpy.props.EnumProperty(
        name="Distance function",
        items=DISTANCE_TYPES,
    )
    uv_source = bpy.props.EnumProperty(
        name="UV source",
        items=uv_source,
    )
    uv_target = bpy.props.EnumProperty(
        name="UV target",
        items=uv_target,
    )


class PAMLayer(bpy.types.PropertyGroup):
    object = bpy.props.StringProperty(
        update=update_object,
    )
    type = bpy.props.EnumProperty(
        items=LAYER_TYPES,
        name="Layer type",
        default=LAYER_TYPES[0][0],
    )
    collapsed = bpy.props.BoolProperty(
        default=True,
    )
    kernel = bpy.props.PointerProperty(type=PAMKernelParameter)
    synapse_count = bpy.props.IntProperty(
        min=1,
        default=1,
    )


class PAMMapSet(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="mapping")
    layers = bpy.props.CollectionProperty(type=PAMLayer)
    mappings = bpy.props.CollectionProperty(type=PAMMappingParameter)


class PAMMap(bpy.types.PropertyGroup):
    sets = bpy.props.CollectionProperty(type=PAMMapSet)
    active_set = bpy.props.IntProperty()
    num_neurons = bpy.props.IntProperty(
        default=1,
        min=1,
    )


class PAMMappingUp(bpy.types.Operator):
    bl_idname = "pam.mapping_up"
    bl_label = "Move mapping up"
    bl_description = ""
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        return len(m.sets) > 1 and m.active_set > 0

    def execute(self, context):
        m = context.scene.pam_mapping

        last = m.active_set - 1

        if last >= 0:
            m.sets.move(m.active_set, last)
            m.active_set = last

        return {'FINISHED'}


class PAMMappingDown(bpy.types.Operator):
    bl_idname = "pam.mapping_down"
    bl_label = "Move mapping down"
    bl_description = ""
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        return len(m.sets) > 1 and m.active_set < len(m.sets) - 1

    def execute(self, context):
        m = context.scene.pam_mapping

        next = m.active_set + 1

        if next < len(m.sets):
            m.sets.move(m.active_set, next)
            m.active_set = next

        return {'FINISHED'}


class PAMMappingLayerUp(bpy.types.Operator):
    bl_idname = "pam.mapping_layer_up"
    bl_label = "Move layer up"
    bl_description = ""
    bl_options = {"UNDO"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        return any(active_set.layers)

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        last = self.index - 1

        if last >= 0:
            active_set.layers.move(self.index, last)
            active_set.mappings.move(self.index, last)

        return {'FINISHED'}


class PAMMappingLayerDown(bpy.types.Operator):
    bl_idname = "pam.mapping_layer_down"
    bl_label = "Move layer down"
    bl_description = ""
    bl_options = {"UNDO"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        return any(active_set.layers)

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        next = self.index + 1

        if next < len(active_set.layers):
            active_set.layers.move(self.index, next)
            active_set.mappings.move(self.index, next)

        return {'FINISHED'}


class PAMMappingLayerAdd(bpy.types.Operator):
    bl_idname = "pam.mapping_layer_add"
    bl_label = "Add layer"
    bl_description = ""
    bl_options = {"UNDO"}

    test123 = bpy.props.EnumProperty(items=LAYER_TYPES)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        l = active_set.layers.add()
        m = active_set.mappings.add()

        return {'FINISHED'}


class PAMMappingLayerRemove(bpy.types.Operator):
    bl_idname = "pam.mapping_layer_remove"
    bl_label = "Remove layer"
    bl_description = ""
    bl_options = {"UNDO"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        set = m.sets[m.active_set]
        return len(set.layers) > 2

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        active_set.layers.remove(self.index)
        active_set.mappings.remove(self.index)

        return {'FINISHED'}


class PAMMappingSetObject(bpy.types.Operator):
    bl_idname = "pam.mapping_layer_set_object"
    bl_label = "Set layer"
    bl_description = ""
    bl_options = {"UNDO"}

    index = bpy.props.IntProperty()

    def execute(self, context):
        active_obj = context.scene.objects.active
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        layer = active_set.layers[self.index]
        layer.object = active_obj.name

        return {'FINISHED'}


class PAMMappingAddSet(bpy.types.Operator):
    bl_idname = "pam.mapping_add_set"
    bl_label = "Add a mapping set"
    bl_description = ""
    bl_options = {"UNDO"}

    count = bpy.props.IntProperty()

    def execute(self, context):
        active_obj = context.scene.objects.active
        m = context.scene.pam_mapping

        set = m.sets.add()
        set.name = "%s.%03d" % (set.name, self.count)
        self.count += 1

        pre = set.layers.add()
        pos = set.layers.add()

        set.mappings.add()
        set.mappings.add()

        return {'FINISHED'}


class PAMMappingDeleteSet(bpy.types.Operator):
    bl_idname = "pam.mapping_delete_set"
    bl_label = "Delete active mapping set"
    bl_description = ""
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return any(context.scene.pam_mapping.sets)

    def execute(self, context):
        context.scene.pam_mapping.sets.remove(context.scene.pam_mapping.active_set)

        return {'FINISHED'}


class PAMMappingSetLayer(bpy.types.Operator):
    bl_idname = "pam.mapping_layer_set"
    bl_label = "Delete active mapping set"
    bl_description = ""
    bl_options = {"UNDO"}

    type = bpy.props.EnumProperty(items=LAYER_TYPES[1:])

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        active_obj = context.scene.objects.active
        m = context.scene.pam_mapping

        active_set = m.sets[m.active_set]

        layer = active_set.layers.add()
        mapping = active_set.mappings.add()

        layer.object = active_obj.name
        layer.type = self.type

        context.scene.objects.active = active_obj

        return {'FINISHED'}


class PAMMappingCompute(bpy.types.Operator):
    bl_idname = "pam.mapping_compute"
    bl_label = "Compute mapping"
    bl_description = ""

    type = bpy.props.EnumProperty(items=LAYER_TYPES[1:])

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        pam.initialize3D()

        for set in bpy.context.scene.pam_mapping.sets:

            pre_neurons = set.layers[0].kernel.particles
            pre_func = set.layers[0].kernel.function
            pre_params = [param.value for param in set.layers[0].kernel.parameters]

            post_neurons = set.layers[-1].kernel.particles
            post_func = set.layers[-1].kernel.function
            post_params = [param.value for param in set.layers[-1].kernel.parameters]

            synapse_layer = -1
            synapse_count = 0
            layers = []

            # collect all
            for i, layer in enumerate(set.layers):
                layers.append(bpy.data.objects[layer.object])
                # if this is the synapse layer, store this
                if layer.type == LAYER_TYPES[3][0]:
                    synapse_layer = i
                    synapse_count = layer.synapse_count

            # error checking procedures
            if synapse_layer == -1:
                raise Exception('no synapse layer given')

            mapping_funcs = []
            distance_funcs = []

            for mapping in set.mappings[:-1]:
                mapping_funcs.append(MAPPING_DICT[mapping.function])
                distance_funcs.append(DISTANCE_DICT[mapping.distance])

            pam.addConnection(
                layers,
                pre_neurons, post_neurons,
                synapse_layer,
                mapping_funcs,
                distance_funcs,
                eval('kernel.' + pre_func),
                pre_params,
                eval('kernel.' + post_func),
                post_params,
                synapse_count
            )

        pam.resetOrigins()
        pam.computeAllConnections()

        return {'FINISHED'}


class PAMMappingComputeSelected(bpy.types.Operator):
    bl_idname = "pam.mapping_compute_sel"
    bl_label = "Compute selected mapping"
    bl_description = ""

    type = bpy.props.EnumProperty(items=LAYER_TYPES[1:])

    @classmethod
    def poll(cls, context):
            return True

    def execute(self, context):
        pam.initialize3D()

        set = bpy.context.scene.pam_mapping.sets[bpy.context.scene.pam_mapping.active_set]

        pre_neurons = set.layers[0].kernel.particles
        pre_func = set.layers[0].kernel.function
        pre_params = [param.value for param in set.layers[0].kernel.parameters]

        post_neurons = set.layers[-1].kernel.particles
        post_func = set.layers[-1].kernel.function
        post_params = [param.value for param in set.layers[-1].kernel.parameters]

        synapse_layer = -1
        synapse_count = 0
        layers = []

        # collect all
        for i, layer in enumerate(set.layers):
            layers.append(bpy.data.objects[layer.object])
            # if this is the synapse layer, store this
            if layer.type == LAYER_TYPES[3][0]:
                synapse_layer = i
                synapse_count = layer.synapse_count

        # error checking procedures
        if synapse_layer == -1:
            raise Exception('no synapse layer given')

        mapping_funcs = []
        distance_funcs = []

        for mapping in set.mappings[:-1]:
            mapping_funcs.append(MAPPING_DICT[mapping.function])
            distance_funcs.append(DISTANCE_DICT[mapping.distance])

        pam.addConnection(
            layers,
            pre_neurons, post_neurons,
            synapse_layer,
            mapping_funcs,
            distance_funcs,
            eval('kernel.' + pre_func),
            pre_params,
            eval('kernel.' + post_func),
            post_params,
            synapse_count
        )

        pam.resetOrigins()
        pam.computeAllConnections()

        return {'FINISHED'}


class PAMAddNeuronSet(bpy.types.Operator):
    """Adds a new neuron set to the active object.

    Note: Only mesh-objects are allowed to own neuron sets as custom
    properties.
    """

    bl_idname = "pam.add_neuron_set"
    bl_label = "Add neuron-set"
    bl_description = "Add a new neuron set"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object.type == "MESH"

    def execute(self, context):
        active_obj = context.active_object
        m = context.scene.pam_mapping

        bpy.ops.object.particle_system_add()

        psys = active_obj.particle_systems[-1]
        psys.name = "pam.neuron_group"
        psys.seed = random.randrange(0, 1000000)

        pset = psys.settings
        pset.type = "EMITTER"
        pset.count = m.num_neurons
        pset.frame_start = pset.frame_end = 1.0
        pset.emit_from = "FACE"
        pset.use_emit_random = True
        pset.use_even_distribution = True
        pset.distribution = "RAND"
        pset.use_rotations = True
        pset.use_rotation_dupli = True
        pset.rotation_mode = "NOR"
        pset.normal_factor = 0.0
        pset.render_type = "OBJECT"
        pset.use_whole_group = True
        pset.physics_type = "NO"
        pset.particle_size = 1.0

        bpy.ops.object.select_all(action="DESELECT")

        context.scene.update()

        context.scene.objects.active = active_obj
        active_obj.select = True

        return {'FINISHED'}


class PAMMappingAddSelfInhibition(bpy.types.Operator):
    """Self-Inhibition Layer"""

    bl_idname = "pam.mapping_self_inhibition"
    bl_label = "Add layer as self-inhibition mapping"
    bl_description = "Add layer as self-inhibition mapping"
    bl_options = {'UNDO'}

    count = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.object.type == "MESH"

    def execute(self, context):
        active_obj = context.scene.objects.active
        m = context.scene.pam_mapping

        newset = m.sets.add()
        newset.name = "selfinhibition.%03d" % self.count
        self.count += 1

        pre = newset.layers.add()
        pre_mapping = newset.mappings.add()
        pre.object = active_obj.name
        pre.type = LAYER_TYPES[5][0]
        pre_mapping.distance = DISTANCE_TYPES[2][0]
        pre_mapping.function = MAPPING_TYPES[3][0]

        syn = newset.layers.add()
        syn_mapping = newset.mappings.add()
        syn.object = active_obj.name
        syn.type = LAYER_TYPES[3][0]
        syn.synapse_count = 10
        syn_mapping.distance = DISTANCE_TYPES[2][0]
        syn_mapping.function = MAPPING_TYPES[3][0]

        post = newset.layers.add()
        post_mapping = newset.mappings.add()
        post.object = active_obj.name
        post.type = LAYER_TYPES[1][0]

        for layer in [pre, post]:
            layer.kernel.object = active_obj.name
            layer.kernel.function = KERNEL_TYPES[1][0]
            layer.kernel.parameters.clear()
            var_u = layer.kernel.parameters.add()
            var_u.name = 'var_u'
            var_u.value = 0.2
            var_v = layer.kernel.parameters.add()
            var_v.name = 'var_v'
            var_v.value = 0.2
            shift_u = layer.kernel.parameters.add()
            shift_u.name = 'shift_u'
            shift_u.value = 0
            shift_v = layer.kernel.parameters.add()
            shift_v.name = 'shift_v'
            shift_v.value = 0
            item = particle_systems(layer.kernel, context)
            if len(item) > 1:
                layer.kernel.particles = item[1][0]

        context.scene.objects.active = active_obj

        return {'FINISHED'}


class PAMMappingUpdate(bpy.types.Operator):
    """Update active mapping"""

    bl_idname = "pam.mapping_update"
    bl_label = "Update active mapping"
    bl_description = "Update active mapping"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        pre_neurons = active_set.layers[0].kernel.particles
        pre_func = active_set.layers[0].kernel.function
        pre_params = [param.value for param in active_set.layers[0].kernel.parameters]

        post_neurons = active_set.layers[-1].kernel.particles
        post_func = active_set.layers[-1].kernel.function
        post_params = [param.value for param in active_set.layers[-1].kernel.parameters]

        synapse_layer = -1
        synapse_count = 0
        layers = []

        # collect all
        for i, layer in enumerate(active_set.layers):
            layers.append(bpy.data.objects[layer.object])
            # if this is the synapse layer, store this
            if layer.type == LAYER_TYPES[3][0]:
                synapse_layer = i
                synapse_count = layer.synapse_count

        # error checking procedures
        if synapse_layer == -1:
            raise Exception('no synapse layer given')

        mapping_funcs = []
        distance_funcs = []

        for mapping in active_set.mappings[:-1]:
            mapping_funcs.append(MAPPING_DICT[mapping.function])
            distance_funcs.append(DISTANCE_DICT[mapping.distance])

        pam.updateConnection(
            m.active_set,
            layers,
            pre_neurons, post_neurons,
            synapse_layer,
            mapping_funcs,
            distance_funcs,
            eval('kernel.' + pre_func),
            pre_params,
            eval('kernel.' + post_func),
            post_params,
            synapse_count
        )

        pam.updateMapping(m.active_set)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(PAMKernelValues)
    bpy.utils.register_class(PAMKernelParameter)
    bpy.utils.register_class(PAMMappingParameter)
    bpy.utils.register_class(PAMLayer)
    bpy.utils.register_class(PAMMapSet)
    bpy.utils.register_class(PAMMap)
    bpy.types.Scene.pam_mapping = bpy.props.PointerProperty(
        type=PAMMap
    )


def unregister():
    del bpy.types.Scene.pam_mapping


def validate_layer(context, layer):
    err = None

    if layer.type == "none":
        err = "layer missing type"

    elif layer.object == "":
        err = "layer missing object"

    elif layer.object not in context.scene.objects:
        err = "layer object missing in scene"

    return err


def validate_mapping(mapping):
    return False
