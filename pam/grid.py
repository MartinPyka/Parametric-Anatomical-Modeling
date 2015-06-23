"""Temporary Helper Module"""

import logging
import math
import numpy

import bpy
import mathutils

from . import constants
from . import helper

#import constants
#import helper

logger = logging.getLogger(__package__)


def uv_bounds(obj):
    """Returns upper uv bounds of an object

    :param bpy.types.Object obj: blender object
    :return: uv coordinates
    :rtype: tuple (float, float)

    :raises TypeError: if obj has no uv data attached

    """
    active_uv = obj.data.uv_layers.active

    if not hasattr(active_uv, "data"):
        logger.error("%s has no uv data", obj)
        raise TypeError("object has no uv data")

    u = max([mesh.uv[0] for mesh in active_uv.data])
    v = max([mesh.uv[1] for mesh in active_uv.data])

    logger.debug("%s uv bounds (%f, %f)", obj, u, v)

    return u, v


def grid_dimension(u, v, res):
    """Calculates grid dimension from upper uv bounds

    :param float u: u coordinate
    :param float v: v coordinate
    :param float res: needed resolution
    :return: row, column count
    :rtype: tuple (int, int)

    :raises ValueError: if uv coordinates exceed 0.0-1.0 range

    """
    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        logger.error("uv coordinate out of bounds (%f, %f)", u, v)
        raise ValueError("uv coordinate out of bounds")

    minor = min(u, v)
    row = math.ceil(1.0 / res)
    col = math.ceil(minor / res)

    if minor is u:
        row, col = col, row

    logger.debug(
        "uv bounds (%f, %f) to grid dimension [%d][%d]",
        u, v, row, col
    )

    return int(row), int(col)


class UVGrid(object):
    """Convenience class to raster and project on uv mesh"""

    def __init__(self, obj, resolution=constants.DEFAULT_RESOLUTION):
        self._obj = obj
        self._scaling = obj['uv_scaling']
        self._resolution = resolution

        self._u, self._v = uv_bounds(obj)
        self._row, self._col = grid_dimension(
            self._u,
            self._v,
            self._resolution
        )

        self.reset_weights()        
        self._uvcoords = [[[] for j in range(self._col)] for i in range(self._row)]
        self._gridmask = [[True for j in range(self._col)] for i in range(self._row)]

        self._masks = {
            "pre": [[[] for j in range(self._col)] for i in range(self._row)],
            "post": [[[] for j in range(self._col)] for i in range(self._row)]
        }

        self._grid = {}

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
        
    def reset_weights(self):
        self._weights = [[[] for j in range(self._col)] for i in range(self._row)]

    # TODO(SK): Missing docstring
    @property
    def dimension(self):
        return (self._row, self._col)

    # TODO(SK): Missing docstring
    @property
    def resolution(self):
        return self._resolution

    # TODO(SK): Missing docstring
    @property
    def uv_bounds(self):
        return self._u, self._v

    # TODO(SK): Missing docstring
    def compute_pre_mask(self, kernel, args):
        self.compute_grid("pre", kernel, args)

    # TODO(SK): Missing docstring
    def compute_post_mask(self, kernel, args):
        self.compute_grid("post", kernel, args)
        self._grid['post'] = [item for sublist in self._grid['post'][:,:] for item in sublist]

    def compute_grid(self, mask, kernel, args = []):
        grid = numpy.zeros((self._row, self._col, self._row, self._col))
        x = numpy.linspace(0., 1., self._row)
        y = numpy.linspace(0., 1., self._col)
        guvs = numpy.dstack(numpy.meshgrid(x, y))[...,::-1]
        for i in range(self._row):
            for j in range(self._col):
                uvs = numpy.array([self._cell_index_to_uv(i, j)])
                # Create array with uv-coords
                grid[i][j] = kernel(uvs, guvs, *args)
        self._grid[mask] = grid

    def insert_postNeuron(self, index, uv, p_3d, d):
        row, col = self._uv_to_cell_index(uv[0], uv[1])
        if row == -1:
            return

        self._masks['post'][row][col].append((index, uv, p_3d, d))
        
    def convert_postNeuronStructure(self):
        """ Needs to be called after all neurons have been inserted (usually, this is
        done in select_random """
        self._masks['post'] = numpy.array([item for sublist in self._masks['post'] for item in sublist])

    def cell(self, u, v):
        """Returns cell for uv coordinate

        :param float u: u coordinate
        :param float v: v coordinate
        :return: cell
        :rtype: list

        """
        row, col = self._uv_to_cell_index(u, v)
        if row == -1:
            return []

        c = self._weights[row][col]

        logger.debug("cell at index [%d][%d]", row, col)

        return c

    def select_random(self, uv, quantity):
        """Returns a set of randomly selected items from uv coordinate
        corresponding cell

        :param uv: uv coordinates
        :type: tuple (float, float)
        :param int quantity: size of set
        :return: randomly selected items
        :rtype: list

        """
        if uv[0] >= self._u or uv[1] >= self._v or uv[0] < 0.0 or uv[1] < 0.0:
            return []

        row, col = self._uv_to_cell_index(uv[0], uv[1])
        if row == -1:
            return []
        
        # check, whether ._mask['post'] has already been converted. If not, convert it
        if len(self._masks['post']) < (self._row * self._col):
            self.convert_postNeuronStructure()

        mask = self._grid['pre'][row][col]
        if len(mask) == 0:
            return []

        weights = mask.flatten()
        indices = numpy.random.choice(len(weights), size = quantity, p = weights / numpy.sum(weights))
        # select post-synaptic cell-array for synapse locations
        selected_cells = numpy.take(self._grid['post'], indices, axis = 0)

        selected = []
        cell_indices = []

        for i, c in enumerate(selected_cells):
            # compute weights for cell
            weights = c.flatten()
            # Multiply by number of cells available
            weights *= [len(cells) for cells in self._masks['post']]
            # select with weighted probabilites one cell-index per cell
            cell_indices.append( numpy.random.choice(len(weights), size = 1, p = weights / numpy.sum(weights))[0] )

        post_cells = numpy.take(self._masks['post'], cell_indices, axis = 0)
        
        # select randomly post-neurons
        for p_cell in post_cells:
            post_neuron = numpy.random.choice(len(p_cell))
            selected.append(p_cell[post_neuron])    

        return selected

    def adjustUV(self, uv):
        """Return adjustd uv coordinates

        :param uv: uv coordinates
        :type uv: tuple (float, float)
        :return: adjusted uv coordinates
        :rtype: tuple (float, float)

        """
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

        row = int(math.floor(u / self._resolution))
        col = int(math.floor(v / self._resolution))

        logger.debug("uv (%f, %f) to cell index [%d][%d]", u, v, row, col)

        return row, col

    def _cell_index_to_uv(self, row, col):
        """Returns uv coordinate from the center of a cell"""
        center = self._resolution / 2
        u = row * self._resolution + center
        v = col * self._resolution + center

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
                self._uvcoords[row][col] = numpy.array((u, v))
                if self._onGrid(numpy.array((u, v))) == 0:
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

        return 1            # TODO: remove afterwards
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
