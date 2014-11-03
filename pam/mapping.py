"""Mapping module"""

import logging

import bpy

logger = logging.getLogger(__package__)


class MappingLayer(bpy.types.PropertyGroup):
    object = bpy.props.EnumProperty(

    )
    mapping_method = bpy.props.EnumProperty(

    )
    distance_method = bpy.props.EnumProperty(

    )


class UVMapLayer(bpy.types.PropertyGroup):
    UV_A = bpy.props.EnumProperty(

    )
    UV_B = bpy.props.EnumProperty(

    )


class PreSynapticLayer(MappingLayer, UVMapLayer):
    particle_system = bpy.props.EnumProperty(

    )
    kernel_function = bpy.props.EnumProperty(

    )
    # TODO(SK): Kernel Parameter


class SynapticLayer(MappingLayer, UVMapLayer):
    synapse_count = bpy.props.IntProperty(

    )


class PostSynapticLayer(MappingLayer):
    particle_system = bpy.props.EnumProperty(

    )
    # TODO(SK): Kernel Parameter


class IntermediateSynapticLayer(MappingLayer, UVMapLayer):
    pass


class MappingProperties(bpy.types.PropertyGroup):
    pass


def register():
    bpy.utils.register_class(MappingProperties)
    bpy.types.Scene.pam_mapping = bpy.props.PointerProperty(
        type=MappingProperties
    )


def unregister():
    del bpy.types.Scene.pam_mapping


def is_mapping_valid():
    pass
