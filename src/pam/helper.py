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

        raster = UVRaster(active_obj)
        print(raster)

        return {'FINISHED'}


# TODO(SK): docstring missing
@utils.profiling
def uv_bounds(obj):
    active_uv = obj.data.uv_layers.active

    if not hasattr(active_uv, "data"):
        raise Exception("%s has no uv data", obj)

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


# TODO(SK): doctstring missing
class UVRaster(object):
    _obj = None
    _list = []
    _res = 0.0
    __x = 0
    __y = 0
    _u = 0.0
    _v = 0.0

    def __init__(self, obj, res=0.01):
        self._obj = obj
        self._res = res

        u, v = uv_bounds(obj)
        x, y = uv_to_matrix_dimension(u, v, res)
        self._u = u
        self._v = v
        self._x = x
        self._y = y

        self._list = [[[] for j in range(y)] for i in range(x)]

    def __del__(self):
        del self._list
        self._obj = None

    def __repr__(self):
        return "<UVRaster dim: %s items: %d, res: %f, max uv: %s>" % \
               (self.dim, self.res, len(self), self.uv_bounds)

    def __getitem__(self, index):
        return self._list[index]

    def __len__(self):
        sum = 0
        for row in self._list:
            for col in row:
                if any(col):
                    sum += len(col)
        return sum

    @property
    def dim(self):
        return self._x, self._y

    @property
    def res(self):
        return self._res

    @property
    def uv_bounds(self):
        return self._u, self._v

    def uv_to_cell(self, u, v):
        if u > self._u or v > self._v or u < 0.0 or v < 0.0:
            raise Exception("uv out of bounds")

        row = math.ceil(u / self._res)
        col = math.ceil(v / self._res)

        logger.debug("uv (%f, %f) to cell [%d][%d]", u, v, row, col)

        return self._list[row][col]
