"""Temporary Helper Module"""

import code
import logging
import math
import random
import types

import bpy
import mathutils

from . import helper

logger = logging.getLogger(__package__)

DEFAULT_LOCATION = mathutils.Vector((0.0, 0.0, 0.0))
DEFAULT_SCALE = mathutils.Vector((1.0, 1.0, 1.0))
DEFAULT_ROTATION = mathutils.Euler((0.0, 0.0, 0.0), "XYZ")

DEFAULT_RESOLUTION = 0.05
KERNEL_THRESHOLD = 0.05


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


class UVGrid(object):
    """Convenience class to raster and project on uv mesh"""
    _weights = None
    _uvcoords = None

    def __init__(self, obj, res=DEFAULT_RESOLUTION):
        self._obj = obj
        self._scaling = obj['uv_scaling']
        self._res = res

        u, v = uv_bounds(obj)
        row, col = uv_to_grid_dimension(u, v, res)
        self._u = u
        self._v = v
        self._row = row
        self._col = col

        self._weights = [[[] for j in range(col)] for i in range(row)]
        self._uvcoords = [[[] for j in range(col)] for i in range(row)]
        self._gridmask = [[True for j in range(col)] for i in range(row)]

        self._pre_kernel = None
        self._pre_kernel_args = None
        self._pre_mask = []

        self._post_kernel = None
        self._post_kernel_args = None
        self._post_mask = []

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
    def dimension(self):
        return mathutils.Vector((self._row, self._col))

    @property
    def resolution(self):
        return self._res

    @property
    def uv_bounds(self):
        return self._u, self._v

    @property
    def pre_kernel(self):
        return self._pre_kernel

    @pre_kernel.setter
    def pre_kernel(self, func):
        if not isinstance(func, types.FunctionType):
            logger.error("kernel must be a function, %s is not", func)
            raise Exception("kernel must be a function")

        self._pre_kernel = func

    @property
    def pre_kernel_args(self):
        return self._pre_kernel_args

    @pre_kernel_args.setter
    def pre_kernel_args(self, args):
        self._pre_kernel_args = args

    @property
    def post_kernel(self):
        return self._post_kernel

    @post_kernel.setter
    def post_kernel(self, func):
        if not isinstance(func, types.FunctionType):
            logger.error("kernel must be a function, %s is not", func)
            raise Exception("kernel must be a function")

        self._post_kernel = func

    @property
    def post_kernel_args(self):
        return self._post_kernel_args

    @post_kernel_args.setter
    def post_kernel_args(self, args):
        self._post_kernel_args = args

    # TODO(SK): missing docstring
    def compute_preMask(self):
        elems = range(int((2. / self._res) + 1))
        shift = int((len(elems) - 1) / 2)
        for r_row in elems:
            for r_col in range(int((2 / self._res) + 1)):
                relativ_row = r_row - shift
                relativ_col = r_col - shift
                v = self._pre_kernel(
                    mathutils.Vector((0, 0)),
                    mathutils.Vector((relativ_row * self._res, relativ_col * self._res)),
                    self._pre_kernel_args)
                if (v > KERNEL_THRESHOLD):
                    self._pre_mask.append((relativ_row, relativ_col, v))

    # TODO(SK): missing docstring
    def compute_postMask(self):
        elems = range(int((2. / self._res) + 1))
        shift = int((len(elems) - 1) / 2)
        for r_row in elems:
            for r_col in range(int((2. / self._res) + 1)):
                relativ_row = r_row - shift
                relativ_col = r_col - shift
                v = self._post_kernel(
                    mathutils.Vector((0, 0)),
                    mathutils.Vector((relativ_row * self._res, relativ_col * self._res)),
                    self._post_kernel_args)

                if (v > KERNEL_THRESHOLD):
                    self._post_mask.append((relativ_row, relativ_col, v))

    def insert_postNeuron(self, index, uv, p_3d, d):
        """Computes weights with current registered kernel across the grid"""
        # self._reset_weights()
        row, col = self._uv_to_cell_index(uv[0], uv[1])
        # if the uv-coordinate is not on the grid, return

        if row == -1:
            return

        for cell in self._post_mask:
            if (row + cell[0] >= 0) & (row + cell[0] < self._row) & (col + cell[1] >= 0) & (col + cell[1] < self._col):
                if self._gridmask[row + cell[0]][col + cell[1]] is True:
                    self._weights[int(row + cell[0])][int(col + cell[1])].append(
                        (index, cell[2], p_3d, d))

    def compute_intersect_premask_weights(self, row, col):
        """ Computes the intersect between premask applied on row and col and
        the weights-array """
        result = []
        for cell in self._pre_mask:
            # if we are in the bords of the grid
            if (row + cell[0] >= 0) & (row + cell[0] < self._row) & (col + cell[1] >= 0) & (col + cell[1] < self._col):
                # if the weight-cell has some entries
                if len(self._weights[int(row + cell[0])][int(col + cell[1])]) > 0:
                    result.append(cell)
        return result

    def cell(self, u, v):
        """Returns cell for uv coordinate"""
        row, col = self._uv_to_cell_index(u, v)
        if row == -1:
            return []

        cell = self._weights[row][col]

        logger.debug("cell at index [%d][%d]", row, col)

        return cell

    def select_random(self, uv, quantity):
        """Returns a number of randomly selected items from uv coordinate
        corresponding cell
        """
        if uv[0] >= self._u or uv[1] >= self._v or uv[0] < 0.0 or uv[1] < 0.0:
            return []

        row, col = self._uv_to_cell_index(uv[0], uv[1])
        if row == -1:
            return []

        mask = self.compute_intersect_premask_weights(row, col)
        if len(mask) == 0:
            return []

        weights = [item[2] for item in mask]
        indices = helper.random_select_indices(weights, quantity)
        selected_cells = [mask[index] for index in indices]

        selected = []

        for cell in selected_cells:
            neurons = self._weights[int(row + cell[0])][int(col + cell[1])]

            n_weights = [neuron[1] for neuron in neurons]
            n_indices = helper.random_select_indices(n_weights, 1)
            selected.append((neurons[n_indices[0]], mathutils.Vector(self._cell_index_to_uv(row + cell[0], col + cell[1]))))

        return selected

    # TODO(SK): missing docstring
    def adjustUV(self, uv):
        if uv[0] >= self._u or vv[1] >= self._v or uv[0] < 0.0 or vv[0] < 0.0:
            uv[0] = min(self._u, max(0., uv[0]))
            uv[1] = min(self._v, max(0., vv[0]))
        return uv

    def _uv_to_cell_index(self, u, v):
        """Returns cell index for a uv coordinate"""
        if u >= self._u or v >= self._v or u < 0.0 or v < 0.0:
            # logger.error("uv coordinate out of bounds (%f, %f)", u, v)
            return -1, -1
            # u = min(self._u, max(0., u))
            # v = min(self._v, max(0., v))

        row = math.floor(u / self._res)
        col = math.floor(v / self._res)

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
                self._uvcoords[row][col] = mathutils.Vector((u, v))
                if self._onGrid(mathutils.Vector((u, v))) == 0:
                    self._gridmask[row][col] = False

    def _reset_weights(self):
        """Resets weights across the grid"""
        self._weights = [[[] for j in range(self._col)]
                         for i in range(self._row)]

    def _onGrid(self, uv):
        """Converts a given UV-coordinate into a 3d point,
        object for the 3d point and object_uv must have the same topology
        if normal is not None, the normal is used to detect the point on object, otherwise
        the closest_point_on_mesh operation is used
        """

        result = 0
        for p in self._obj.data.polygons:
            uvs = [self._obj.data.uv_layers.active.data[li] for li in p.loop_indices]
            result = mathutils.geometry.intersect_point_tri_2d(
                uv,
                uvs[0].uv,
                uvs[1].uv,
                uvs[2].uv
            )

            if (result == 1) | (result == -1):
                result = 1
                break
            else:
                result = mathutils.geometry.intersect_point_tri_2d(
                    uv,
                    uvs[0].uv,
                    uvs[2].uv,
                    uvs[3].uv
                )

                if (result == 1) | (result == -1):
                    result = 1
                    break

        return result
