"""Visualization Module"""

import logging

import bpy

logger = logging.getLogger(__package__)


# TODO(SK): missing docstring
class PAMVisualizeKernel(bpy.types.Operator):

    bl_idname = "pam.visualize_kernel"
    bl_label = "Visualize kernel"
    bl_description = "Visualize kernel function on object"
    bl_options = {'UNDO'}


class VisualizeKernelProperties(bpy.types.PropertyGroup):
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


def register():
    bpy.utils.register_class(VisualizeKernelProperties)
    bpy.types.Scene.pam_visualize = bpy.props.PointerProperty(
        type=VisualizeKernelProperties
    )


def unregister():
    del bpy.types.Scene.pam_visualize
