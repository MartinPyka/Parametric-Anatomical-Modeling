"""Mapping module"""

import logging

import bpy

from . import kernel

logger = logging.getLogger(__package__)

LAYER_TYPES = [
    ("none", "None", "", "", 0),
    ("postsynapse", "Postsynapse", "", "", 1),
    ("postintermediates", "Postintermediate", "", "", 2),
    ("synapse", "Synapse", "", "", 3),
    ("preintermediates", "Preintermediate", "", "", 4),
    ("presynapse", "Presynapse", "", "", 5),
]

MAPPING_TYPES = [
    ("none", "None", "", "", 0),
    ("uv", "UV", "", "", 1),
    ("method2", "Method 2", "", "", 2),
]

DISTANCE_TYPES = [
    ("none", "None", "", "", 0),
    ("method1", "Method 1", "", "", 1),
    ("method2", "Method 2", "", "", 2),
]

FAKE_PARTICLES = [
    ("none", "None", "", "", 0),
    ("system1", "System 1", "", "", 1),
    ("system2", "System 2", "", "", 2),
]


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
    function = bpy.props.EnumProperty(
        name="Kernel function",
        items=kernel.KERNEL_TYPES,
    )
    parameters = bpy.props.CollectionProperty(
        type=PAMKernelValues
    )
    particles = bpy.props.EnumProperty(
        name="Particle system",
        items=FAKE_PARTICLES,
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
        items=[]
    )
    uv_target = bpy.props.EnumProperty(
        name="UV target",
        items=[]
    )


class PAMLayer(bpy.types.PropertyGroup):
    object = bpy.props.StringProperty()
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
