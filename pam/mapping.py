"""Mapping module"""

import logging

import bpy

logger = logging.getLogger(__package__)


class PreSynapticLayer(bpy.types.PropertyGroup):
    object_name = bpy.props.StringProperty()
    uv_from = bpy.props.EnumProperty(
        items=[]
    )
    uv_to = bpy.props.EnumProperty(
        items=[]
    )
    mapping = bpy.props.EnumProperty(
        items=[]
    )
    distance = bpy.props.EnumProperty(
        items=[]
    )
    particle_system = bpy.props.EnumProperty(
        items=[]
    )
    kernel_function = bpy.props.EnumProperty(
        items=[]
    )
    # TODO(SK): Kernel Parameter


class SynapticLayer(bpy.types.PropertyGroup):
    object_name = bpy.props.StringProperty()
    synapse_count = bpy.props.IntProperty(

    )
    uv_from = bpy.props.EnumProperty(
        items=[]
    )
    uv_to = bpy.props.EnumProperty(
        items=[]
    )
    mapping = bpy.props.EnumProperty(
        items=[]
    )
    distance = bpy.props.EnumProperty(
        items=[]
    )


class PostSynapticLayer(bpy.types.PropertyGroup):
    object_name = bpy.props.StringProperty()
    particle_system = bpy.props.EnumProperty(
        items=[]
    )
    kernel_function = bpy.props.EnumProperty(
        items=[]
    )
    # TODO(SK): Kernel Parameter


class IntermediateSynapticLayer(bpy.types.PropertyGroup):
    object_name = bpy.props.StringProperty()
    uv_from = bpy.props.EnumProperty(
        items=[]
    )
    uv_to = bpy.props.EnumProperty(
        items=[]
    )
    mapping = bpy.props.EnumProperty(
        items=[]
    )
    distance = bpy.props.EnumProperty(
        items=[]
    )


class MappingProperties(bpy.types.PropertyGroup):
    presynapse = bpy.props.PointerProperty(type=PreSynapticLayer)
    postsynapse = bpy.props.PointerProperty(type=PostSynapticLayer)
    synapse = bpy.props.PointerProperty(type=SynapticLayer)

    preintermediates = bpy.props.CollectionProperty(type=IntermediateSynapticLayer)
    postintermediates = bpy.props.CollectionProperty(type=IntermediateSynapticLayer)
    active_preintermediates = bpy.props.IntProperty()
    active_postintermediates = bpy.props.IntProperty()


def register():
    bpy.utils.register_class(PreSynapticLayer)
    bpy.utils.register_class(PostSynapticLayer)
    bpy.utils.register_class(SynapticLayer)
    bpy.utils.register_class(IntermediateSynapticLayer)
    bpy.utils.register_class(MappingProperties)
    bpy.types.Scene.pam_mapping = bpy.props.PointerProperty(
        type=MappingProperties
    )


def unregister():
    del bpy.types.Scene.pam_mapping


def is_mapping_valid():
    pass
