"""Temporary Helper Module"""

import logging
import math
import types

import bpy
import mathutils

from . import utils

logger = logging.getLogger(__package__)

DEFAULT_LOCATION = mathutils.Vector((0.0, 0.0, 0.0))
DEFAULT_SCALE = mathutils.Vector((1.0, 1.0, 1.0))
DEFAULT_ROTATION = mathutils.Euler((0.0, 0.0, 0.0), "XYZ")

KERNEL_THRESHOLD = 0.5


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

        # raster = UVGrid(active_obj)
        print(transformed_objects())

        return {'FINISHED'}


def transformed_objects():
    """Returns a list of all objects with transformation modifiers applied"""
    objects = bpy.data.objects
    transformed = []

    for obj in objects:
        is_relocated = obj.location != DEFAULT_LOCATION
        is_scaled = obj.scale != DEFAULT_SCALE
        is_rotated = obj.rotation_euler != DEFAULT_ROTATION
        if is_relocated or is_scaled or is_rotated:
            transformed.append(obj)

            logger.debug(
                "%s is transformed, location: %s scale: %s rotation %s",
                obj, obj.location, obj.scale, obj.rotation_euler
            )

    return transformed


def uv_pixel_values(image, u, v):
    """Returns rgba value at uv coordinate from an image"""
    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        logger.error("uv coordinate out of bounds (%f, %f)", u, v)
        raise Exception("UV coordinate are out of bounds")

    if not image.generated_type == "UV_GRID":
        logger.error("images is not of generated_type UV_GRID")
        raise Exception("Images is not a uv image")

    width, height = image.size
    x = int(math.floor(u * width))
    y = int(math.floor(v * height))

    index = (x + y * width) * 4
    r, g, b, a = image.pixels[index:index+4]

    logger.debug(
        "uv (%f,%f) to img xy (%d, %d) at index %d with rgba (%f, %f, %f, %f)",
        u, v, x, y, index, r, g, b, a
    )

    return r, g, b, a


def uv_bounds(obj):
    """Returns upper uv bounds of an object"""
    active_uv = obj.data.uv_layers.active

    if not hasattr(active_uv, "data"):
        logger.error("%s has no uv data", obj)
        raise Exception("object no uv data")

    u = max([mesh.uv[0] for mesh in active_uv.data])
    v = max([mesh.uv[1] for mesh in active_uv.data])

    logger.debug("%s uv bounds (%f, %f)", obj, u, v)

    return u, v


def uv_to_grid_dimension(u, v, res):
    """Calculates grid dimension from upper uv bounds"""
    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        logger.error("uv coordinate out of bounds (%f, %f)", u, v)
        raise Exception("UV coordinate are out of bounds")

    minor = min(u, v)
    row = math.ceil(1.0 / res)
    col = math.ceil(minor / res)

    if minor is u:
        row, col = col, row

    logger.debug(
        "uv bounds (%f, %f) to grid dimension [%d][%d]",
        u, v, row, col
    )

    return row, col


def gaussian_kernel(x, y, origin_x, origin_y, var_x, var_y):
    """Computes distribution value in two dimensional gaussian kernel"""
    return math.exp(-((x - origin_x) ** 2 / (2 * var_x ** 2) +
                      (y - origin_y) ** 2 / (2 * var_y ** 2)))


class UVGrid(object):
    """Convenience class to raster and project on uv mesh"""
    _weights = None
    _uvcoords = None

    def __init__(self, obj, res=0.01):
        self._obj = obj
        self._res = res

        u, v = uv_bounds(obj)
        row, col = uv_to_grid_dimension(u, v, res)
        self._u = u
        self._v = v
        self._row = row
        self._col = col

        self._weights = [[[] for j in range(col)] for i in range(row)]
        self._uvcoords = [[[] for j in range(col)] for i in range(row)]

        self._kernel = None

        self._compute_uvcoords()

    def __del__(self):
        del self._weights
        self._obj = None

    def __repr__(self):
        return "<UVRaster uv: %s resolution: %f dimension: %s items: %d>" % \
               (self.uv_bounds, self.resolution, self.dimension, len(self))

    def __getitem__(self, index):
        return self._weights[index]

    def __setitem__(self, index):
        pass

    def __len__(self):
        return any([len(c) for r in self._weights for c in r if any(c)])

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
        if not isinstance(func, types.FunctionType):
            logger.error("kernel must be a function, %s is not", func)
            raise Exception("kernel must be a function")

        self._kernel = func

    def compute_kernel(self, index, *args, **kwargs):
        """Computes weights with current registered kernel across the grid"""
        self._reset_weights()

        for row in range(self._row):
            for col in range(self._col):
                u, v = self._uvcoords[row][col]
                weight = self._kernel(u, v, *args, **kwargs)

                logger.debug(
                    "%s(%s, %s) at cell [%d][%d] with weight (%f)",
                    self._kernel.__name__, args, kwargs, row, col, weight
                )

                if weight > KERNEL_THRESHOLD:
                    self._weights[row][col].append((index, weight))

    def cell(self, u, v):
        """Returns cell for uv coordinate"""
        row, col = self._uv_to_cell_index(u, v)
        cell = self._objects[row][col]

        logger.debug("cell at index [%d][%d]", row, col)

        return cell

    def _uv_to_cell_index(self, u, v):
        """Returns cell index for a uv coordinate"""
        if u > self._u or v > self._v or u < 0.0 or v < 0.0:
            logger.error("uv coordinate out of bounds (%f, %f)", u, v)
            raise Exception("uv coordinate out of bounds")

        row = math.ceil(u / self._res)
        col = math.ceil(v / self._res)

        logger.debug("uv (%f, %f) to cell index [%d][%d]", u, v, row, col)

        return row, col

    def _cell_index_to_uv(self, row, col):
        """Returns uv coordinate from the center of a cell"""
        center = self._res / 2
        u = row * self._res + center
        v = col * self._res + center

        logger.debug(
            "cell index [%d][%d] to center uv (%f, %f)",
            row, col, u, v
        )

        return u, v

    def _compute_uvcoords(self):
        """Computes corresponding uv coordinate across grid"""
        for row in range(self._row):
            for col in range(self._col):
                u, v = self._cell_index_to_uv(row, col)
                self._uvcoords[row][col] = (u, v)

    def _reset_weights(self):
        """Resets weights across the grid"""
        self._weights = [[[] for j in range(self._col)]
                         for i in range(self._row)]
