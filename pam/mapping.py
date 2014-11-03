"""Mapping module"""

import logging

import bpy

logger = logging.getLogger(__package__)


class MappingLayer(bpy.types.PropertyGroup):
    object = bpy.props.EnumProperty(
        items=[]
    )
    mapping_method = bpy.props.EnumProperty(
        items=[]
    )
    distance_method = bpy.props.EnumProperty(
        items=[]
    )


class UVMapLayer(bpy.types.PropertyGroup):
    UV_A = bpy.props.EnumProperty(
        items=[]
    )
    UV_B = bpy.props.EnumProperty(
        items=[]
    )


class PreSynapticLayer(MappingLayer, UVMapLayer, bpy.types.PropertyGroup):
    particle_system = bpy.props.EnumProperty(
        items=[]
    )
    kernel_function = bpy.props.EnumProperty(
        items=[]
    )
    # TODO(SK): Kernel Parameter


class SynapticLayer(MappingLayer, UVMapLayer, bpy.types.PropertyGroup):
    synapse_count = bpy.props.IntProperty(

    )


class PostSynapticLayer(MappingLayer, bpy.types.PropertyGroup):
    particle_system = bpy.props.EnumProperty(
        items=[]
    )
    # TODO(SK): Kernel Parameter


class IntermediateSynapticLayer(bpy.types.PropertyGroup):
    pass


class MappingProperties(bpy.types.PropertyGroup):
    presynapse = bpy.props.PointerProperty(type=PreSynapticLayer)
    postsynapse = bpy.props.PointerProperty(type=PostSynapticLayer)
    synapse = bpy.props.PointerProperty(type=SynapticLayer)

    preintermediates = bpy.props.CollectionProperty(type=IntermediateSynapticLayer)
    postintermediates = bpy.props.CollectionProperty(type=IntermediateSynapticLayer)


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
