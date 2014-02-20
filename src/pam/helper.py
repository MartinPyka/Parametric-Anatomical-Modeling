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

        x, y = uvpoint_from_origin_with_dist(active_obj, (0.3, 0.5), None)

        return {'FINISHED'}


# TODO(SK): missing docstring
@utils.profiling
def rasterize_uv(obj, resolution):
    pass


# TODO(SK): missing docstring
# TODO(SK): needs implementation
@utils.profiling
def uvpoint_from_origin_with_dist(obj, origin, dist_func):
    x_max, y_max = uv_bounds(obj)
    x, y = origin

    x_random = 0.0
    y_random = 0.0

    logger.debug(
        "x: %f, y: %f, rx: %f, ry: %f, dist_func: %s",
        x,
        y,
        x_random,
        y_random,
        dist_func
    )

    return None, None


# TODO(SK): missing docstring
@utils.profiling
def uv_bounds(obj):
    active_uv = obj.data.uv_layers.active

    if not hasattr(active_uv, "data"):
        raise Exception("%s has no uv data", obj)

    x_values = [mesh.uv[0] for mesh in active_uv.data]
    y_values = [mesh.uv[1] for mesh in active_uv.data]

    x_max = max(x_values)
    y_max = max(y_values)

    logger.debug("max(x): %f, max(y): %f", x_max, y_max)

    return x_max, y_max
