"""Temporary Helper Module"""

import logging
import math

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

        raster = UVGrid(active_obj)

        return {'FINISHED'}


# TODO(SK): docstring missing
@utils.profiling
def uv_bounds(obj):
    active_uv = obj.data.uv_layers.active

    if not hasattr(active_uv, "data"):
        logger.error("%s has no uv data", obj)
        raise Exception("object no uv data")

    u = max([mesh.uv[0] for mesh in active_uv.data])
    v = max([mesh.uv[1] for mesh in active_uv.data])

    logger.debug("%s uv bounds (%f, %f)", obj, u, v)

    return u, v


# TODO(SK): docstring missing
@utils.profiling
def uv_to_matrix_dimension(u, v, res):
    minor = min(u, v)
    row = math.ceil(1.0 / res)
    col = math.ceil(minor / res)

    if minor is u:
        tmp = row
        row = col
        col = tmp

    logger.debug(
        "uv bounds (%f, %f) to matrix dimension [%d][%d]",
        u, v, row, col
    )

    return row, col


# TODO(SK): needs implementation
# TODO(SK): docstring missing
@utils.profiling
def kernel_gaussian(x, y, vx, vy, sx, sy):
    return 0.0


class UVGrid(object):
    """Convenience class to raster and project on uv mesh"""
    _objects = None
    _weights = None

    def __init__(self, obj, res=0.01):
        self._obj = obj
        self._res = res

        u, v = uv_bounds(obj)
        row, col = uv_to_matrix_dimension(u, v, res)
        self._u = u
        self._v = v
        self._row = row
        self._col = col

        for l in [self._objects, self._weights]:
            l = [[[] for j in range(col)] for i in range(row)]

    def __del__(self):
        del self._objects
        del self._weights
        self._obj = None

    def __repr__(self):
        return "<UVRaster uv: %s resolution: %f dimension: %s items: %d>" % \
               (self.uv_bounds, self.resolution, self.dimension, len(self))

    def __getitem__(self, index):
        return self._objects[index]

    def __len__(self):
        sum = 0
        for row in self._objects:
            for col in row:
                if any(col):
                    sum += len(col)
        return sum

    @property
    def dimensions(self):
        return self._row, self._col

    @property
    def resolution(self):
        return self._res

    @property
    def uv_bounds(self):
        return self._u, self._v

    @property
    def kernel(self):
        return self._kernel

    @kernel.setter
    def kernel(self, func):
        self._kernel = func

    # TODO(SK): missing docstring
    def compute_kernel(self, u, v):
        pass

    def cell(self, u, v):
        """Returns cell for uv coordinate"""
        row, col = self._uv_to_cell_index(u, v)
        cell = self._objects[row][col]

        logger.debug("cell at index [%d][%d]", row, col)

        return cell

    def cell_with_weight(self, u, v):
        """Returns cell for uv coordinate with distribution weight"""
        row, col = self._uv_to_cell_index(u, v)
        cell = self._objects[row][col]
        weight = self._weights[row][col]

        logger.debug(
            "cell at index [%d][%d] with weight (%f)",
            row, col, weight
        )

        return cell, weight

    def _uv_to_cell_index(self, u, v):
        """Returns cell index for a uv coordinate"""
        if u > self._u or v > self._v or u < 0.0 or v < 0.0:
            logger.error("uv coordinates out of bounds (%f, %f)", u, v)
            raise Exception("uv coordinates out of bounds")

        row = math.ceil(u / self._res)
        col = math.ceil(v / self._res)

        logger.debug("uv (%f, %f) to cell index [%d][%d]", u, v, row, col)

        return row, col

    def _cell_index_to_uv(self, row, col):
        """Returns uv coordinates of the center of a cell"""
        center = self._res / 2
        u = row * self._res + center
        v = col * self._res + center

        logger.debug(
            "cell index [%d][%d] to center uv (%f, %f)",
            row, col, u, v
        )

        return u, v
