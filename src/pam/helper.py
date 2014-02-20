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

    u_values = [mesh.uv[0] for mesh in active_uv.data]
    v_values = [mesh.uv[1] for mesh in active_uv.data]
    u_max = max(u_values)
    v_max = max(v_values)
    logger.debug("max(u): %f, max(v): %f", u_max, v_max)

    return u_max, v_max


# TODO(SK): docstring missing
@utils.profiling
def dimension_raster(x, y, res):
    minor = min(x, y)

    dim1 = math.ceil(1.0 / res)
    dim2 = math.ceil(minor / res)

    if minor is y:
        logger.debug("x: %d y: %d", dim1, dim2)
        return dim1, dim2
    else:
        logger.debug("x: %d y: %d", dim2, dim1)
        return dim2, dim1


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
        x, y = dimension_raster(u, v, res)

        self._u = u
        self._v = v
        self._x = x
        self._y = y

        self._list = [[[] for j in range(y)] for i in range(x)]
        print(self._list)

    def __del__(self):
        del self._list
        self._obj = None

    def __repr__(self):
        return "<UVRaster dim: %s len: %d, res: %f, max uv: %s>" % \
               (self.dim, self.res, len(self), self.uv)

    # TODO(SK): needs implementation
    def __str__(self):
        return self.__repr__()

    def __getitem__(self, index):
        if len(index) is not 2:
            raise Exception("Index has to be a two-dimensional tuple")

        x, y = index
        if x >= self._x | y >= self._y:
            raise IndexError("Index out of range for %s")

        return self._list[x][y]

    # TODO(SK): test! (bug!)
    def __nonzero__(self):
        return any([any(sublist) for sublist in self._list])

    # TODO(SK): test! (bug!)
    def __len__(self):
        return sum([len(sublist) for sublist in self._list])

    @property
    def dim(self):
        return self._x, self._y

    @property
    def res(self):
        return self._res

    @property
    def uv(self):
        return self._u, self._v
