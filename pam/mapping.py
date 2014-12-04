"""Mapping module"""

import logging

import bpy

from . import kernel

logger = logging.getLogger(__package__)

LAYER_TYPES = [
    ("postsynapse", "(5) Postsynapse", "", 5),
    ("postintermediates", "(4) Postintermediate", "", 4),
    ("synapse", "(3) Synapse", "", 3),
    ("preintermediates", "(2) Preintermediate", "", 2),
    ("presynapse", "(1) Presynapse", "", 1),
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
    kernel_function = bpy.props.EnumProperty(
        items=kernel.KERNEL_TYPES
    )
    kernel_parameter = bpy.props.CollectionProperty(
        type=PAMKernelValues
    )


class PAMMappingParameter(bpy.types.PropertyGroup):
    distance_function = bpy.props.EnumProperty(
        items=[]
    )
    mapping_function = bpy.props.EnumProperty(
        items=[]
    )
    uv_source = bpy.props.EnumProperty(
        items=[]
    )
    uv_target = bpy.props.EnumProperty(
        items=[]
    )


class PAMPreSynapticLayer(bpy.types.PropertyGroup):
    object = bpy.props.StringProperty()
    kernel = bpy.props.PointerProperty(type=PAMKernelParameter)
    mapping = bpy.props.PointerProperty(type=PAMMappingParameter)
    particle_system = bpy.props.EnumProperty(
        items=[]
    )


class PAMSynapticLayer(bpy.types.PropertyGroup):
    object = bpy.props.StringProperty()
    mapping = bpy.props.PointerProperty(type=PAMMappingParameter)
    synapse_count = bpy.props.IntProperty()


class PAMPostSynapticLayer(bpy.types.PropertyGroup):
    object = bpy.props.StringProperty()
    kernel = bpy.props.PointerProperty(type=PAMKernelParameter)
    particle_system = bpy.props.EnumProperty(
        items=[]
    )


class PAMIntermediateSynapticLayer(bpy.types.PropertyGroup):
    object = bpy.props.StringProperty()
    mapping = bpy.props.PointerProperty(type=PAMMappingParameter)


class PAMMappingSet(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="mapping")

    presynapse = bpy.props.PointerProperty(type=PAMPreSynapticLayer)
    postsynapse = bpy.props.PointerProperty(type=PAMPostSynapticLayer)
    synapse = bpy.props.PointerProperty(type=PAMSynapticLayer)

    preintermediates = bpy.props.CollectionProperty(type=PAMIntermediateSynapticLayer)
    postintermediates = bpy.props.CollectionProperty(type=PAMIntermediateSynapticLayer)

    active_preintermediate = bpy.props.IntProperty()
    active_postintermediate = bpy.props.IntProperty()


class PAMMapping(bpy.types.PropertyGroup):
    sets = bpy.props.CollectionProperty(type=PAMMappingSet)
    active_set = bpy.props.IntProperty()


class PAMMappingSetLayer(bpy.types.Operator):
    bl_idname = "pam.mapping_set_layer"
    bl_label = "Set mapping layer"
    bl_description = ""

    layer = bpy.props.EnumProperty(
        items=LAYER_TYPES,
    )

    @classmethod
    def poll(cls, context):
        return any(context.scene.pam_mapping.sets)

    def execute(self, context):
        active_obj = context.active_object
        active_set = context.scene.pam_mapping.sets[context.scene.pam_mapping.active_set]
        active_layer = getattr(active_set, self.layer)

        if self.layer.endswith("synapse"):
            active_layer.object = active_obj.name

        elif self.layer.endswith("intermediates"):
            new_layer = active_layer.add()
            new_layer.object = active_obj.name

        else:
            logger.Error("Unknown layer type")
            return {'CANCELLED'}

        context.scene.objects.active = active_obj

        return {'FINISHED'}


class PAMMappingAddSet(bpy.types.Operator):
    bl_idname = "pam.mapping_add_set"
    bl_label = "Add a mapping set"
    bl_description = ""

    def execute(self, context):
        context.scene.pam_mapping.sets.add()

        return {'FINISHED'}


class PAMMappingDeleteSet(bpy.types.Operator):
    bl_idname = "pam.mapping_delete_set"
    bl_label = "Delete active mapping set"
    bl_description = ""

    def execute(self, context):
        context.scene.pam_mapping.sets.remove(context.scene.pam_mapping.active_set)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(PAMKernelValues)
    bpy.utils.register_class(PAMKernelParameter)
    bpy.utils.register_class(PAMMappingParameter)
    bpy.utils.register_class(PAMPreSynapticLayer)
    bpy.utils.register_class(PAMPostSynapticLayer)
    bpy.utils.register_class(PAMSynapticLayer)
    bpy.utils.register_class(PAMIntermediateSynapticLayer)
    bpy.utils.register_class(PAMMappingSet)
    bpy.utils.register_class(PAMMapping)
    bpy.types.Scene.pam_mapping = bpy.props.PointerProperty(
        type=PAMMapping
    )


def unregister():
    del bpy.types.Scene.pam_mapping


def is_mapping_valid():
    pass
