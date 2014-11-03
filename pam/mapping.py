"""Mapping module"""

import logging

import bpy

logger = logging.getLogger(__package__)


class MappingProperties(bpy.types.PropertyGroup):
    pass


def register():
    bpy.utils.register_class(MappingProperties)
    bpy.types.Scene.pam_mapping = bpy.props.PointerProperty(
        type=MappingProperties
    )


def unregister():
    del bpy.types.Scene.pam_mapping
