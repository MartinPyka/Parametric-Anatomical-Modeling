"""Temporary Helper Module"""

import logging

import bpy

from . import utils

logger = logging.getLogger(__package__)


class PAMTestPanel(bpy.types.Panel):
    """Test Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "PAM Testing Tools"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(
            "pam.test_operator",
        )


class PAMTestOperator(bpy.types.Operator):
    """Test Operator"""

    bl_idname = "pam.test_operator"
    bl_label = "Rasterize uv"
    bl_description = "Testing"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        active_obj = context.active_object

        rasterize_uv(active_obj, None)

        result = {'FINISHED'}
        logger.debug("%s: %s", self.__class__.__name__, result)
        return result


# TODO(SK): rasterize_uv missing docstring
@utils.profiling
def rasterize_uv(obj, resolution):
    pass


# TODO(SK): rand_uvpoint_from_origin missing docstring
@utils.profiling
def rand_uvpoint_from_origin(obj, origin, func):
    obj.data.uv_layers.active.data
