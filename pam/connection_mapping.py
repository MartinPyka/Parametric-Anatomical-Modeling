import logging

import mathutils
import random
import numpy
from .mesh import *
from .constants import *

logger = logging.getLogger(__package__)

def computePoint(v1, v2, v3, v4, x1, x2):
    """Interpolates point on a quad
    :param v1, v2, v3, v4: Vertices of the quad
    :type v1, v2, v3, v4: mathutils.Vector
    :param x1, x2: The interpolation values
    :type x1, x2: float [0..1]"""
    mv12_co = v1.co * x1 + v2.co * (1 - x1)
    mv34_co = v3.co * (1 - x1) + v4.co * x1
    mv_co = mv12_co * x2 + mv34_co * (1 - x2)

    return mv_co

def selectRandomPoint(obj):
    """Selects a random point on the mesh of an object

    :param obj: The object from which to select
    :type obj: bpy.types.Object"""
    # select a random polygon
    p_select = random.random() * obj['area_sum']
    polygon = obj.data.polygons[
        numpy.nonzero(numpy.array(obj['area_cumsum']) > p_select)[0][0]]

    # define position on the polygon
    vert_inds = polygon.vertices[:]
    poi = computePoint(obj.data.vertices[vert_inds[0]],
                       obj.data.vertices[vert_inds[1]],
                       obj.data.vertices[vert_inds[2]],
                       obj.data.vertices[vert_inds[3]],
                       random.random(), random.random())

    p, n, f = obj.closest_point_on_mesh(poi)

    return p, n, f



class MappingException(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "MappingException"

class Mapping():
    def __init__(self, layers, connections, distances, debug = False):
        self.layers = layers
        self.connections = connections
        self.distances = distances
        self.debug = debug
        self.initFunctions()

    def initFunctions(self):
        self.mapping_functions = [connection_dict[i] for i in self.connections]
        self.distance_functions = [distance_dict[self.connections[i]][self.distances[i]] for i in range(len(self.distances))]
        self.distance_functions[-1] = distance_dict_syn[self.connections[-1]][self.distances[-1]]

    def computeMapping(self, point):
        self.p3d = [point]

        for i in range(0, len(self.connections)):
            layer = self.layers[i]
            layer_next = self.layers[i + 1]
            con_func = self.mapping_functions[i]
            dis_func = self.distance_functions[i]
            try:
                p3d_n = con_func(self, layer, layer_next, dis_func)
            except MappingException:
                if self.debug:
                    return p3d, i, None
                else:
                    return None, None, None

        # for the synaptic layer, compute the uv-coordinates
        p2d = layer_next.map3dPointToUV(p3d_n)

        return self.p3d, p2d, compute_path_length(self.p3d)



"""Euclidean mapping"""
def con_euclid(self, layer, layer_next, dis_func):
    p3d_n = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    dis_func(self, p3d_n, layer, layer_next)
    return p3d_n

def euclid_dis_euclid(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def euclid_dis_euclid_uv(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def euclid_dis_jump_uv(self, p3d_n, layer, layer_next):
    self.self, p3d.append(p3d_n)
def euclid_dis_uv_jump(self, p3d_n, layer, layer_next):
    p3d_t = layer.map3dPointTo3d(layer, p3d_n)
    self.p3d = self.p3d + layer.interpolateUVTrackIn3D(self.p3d[-1], p3d_t)
    self.p3d.append(p3d_n)
def euclid_dis_normal_uv(self, p3d_n, layer, layer_next):
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    p3d_t = layer_next.map3dPointTo3d(layer_next, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d.append(p3d_t)
    self.p3d = self.p3d + layer_next.interpolateUVTrackIn3D(p3d_t, p3d_n)
    self.p3d.append(p3d_n)
def euclid_dis_uv_normal(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
# If before the synaptic layer
def euclid_dis_euclid_syn(self, p3d_n, layer, layer_next):
    pass
def euclid_dis_euclid_uv_syn(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def euclid_dis_jump_uv_syn(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def euclid_dis_uv_jump_syn(self, p3d_n, layer, layer_next):
    pass
def euclid_dis_normal_uv_syn(self, p3d_n, layer, layer_next):
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    p3d_t = layer_next.map3dPointTo3d(layer_next, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d.append(p3d_t)
def euclid_dis_uv_normal_syn(self, p3d_n, layer, layer_next):
    pass

"""Normal Mapping"""
def con_normal(self, layer, layer_next, dis_func):
    # compute normal on layer for the last point
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    # determine new point
    p3d_n = layer_next.map3dPointTo3d(layer_next, p, n)
    # if there is no intersection, abort
    if p3d_n is None:
        raise MappingException()
    dis_func(self, p3d_n, layer, layer_next)
    return p3d_n

def normal_dis_euclid(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def normal_dis_euclid_uv(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def normal_dis_jump_uv(self, p3d_n, layer, layer_next):
    p3d_t = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    self.p3d.append(p3d_t)
    self.p3d = self.p3d + layer_next.interpolateUVTrackIn3D(p3d_t, p3d_n)
    self.p3d.append(p3d_n)
def normal_dis_uv_jump(self, p3d_n, layer, layer_next):
    p3d_t = layer.map3dPointTo3d(layer, p3d_n)
    self.p3d = self.p3d + layer.interpolateUVTrackIn3D(self.p3d[-1], p3d_t)
    self.p3d.append(p3d_n)
def normal_dis_normal_uv(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def normal_dis_uv_normal(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)

def normal_dis_euclid_syn(self, p3d_n, layer, layer_next):
    pass
def normal_dis_euclid_uv_syn(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def normal_dis_jump_uv_syn(self, p3d_n, layer, layer_next):
    p3d_t = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    self.p3d.append(p3d_t)
def normal_dis_uv_jump_syn(self, p3d_n, layer, layer_next):
    pass
def normal_dis_normal_uv_syn(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def normal_dis_uv_normal_syn(self, p3d_n, layer, layer_next):
    pass

"""Random Mapping"""
def con_random(self, layer, layer_next, dis_func):
    p3d_n, _, _ = selectRandomPoint(layer_next.obj)
    dis_func(self, p3d_n, layer, layer_next)
    return p3d_n

def random_dis_euclid(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def random_dis_euclid_uv(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def random_dis_jump_uv(self, p3d_n, layer, layer_next):
    p3d_t = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    self.p3d.append(p3d_t)
    self.p3d = self.p3d + layer_next.interpolateUVTrackIn3D(p3d_t, p3d_n)
    self.p3d.append(p3d_n)
def random_dis_uv_jump(self, p3d_n, layer, layer_next):
    p3d_t = layer.map3dPointTo3d(layer, p3d_n)
    self.p3d = self.p3d + layer.interpolateUVTrackIn3D(self.p3d[-1], p3d_t)
    self.p3d.append(p3d_n)
def random_dis_normal_uv(self, p3d_n, layer, layer_next):
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    p3d_t = layer_next.map3dPointTo3d(layer_next, p, n)
    self.p3d.append(p3d_t)
    self.p3d = self.p3d + layer_next.interpolateUVTrackIn3D(p3d_t, p3d_n)
    self.p3d.append(p3d_n)
def random_dis_uv_normal(self, p3d_n, layer, layer_next):
    p, n, f = layer_next.closest_point_on_mesh(p3d_n)
    p3d_t = layer.map3dPointTo3d(layer, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d = self.p3d + layer.interpolateUVTrackIn3D(self.p3d[-1], p3d_t)
    self.p3d.append(p3d_t)
    self.p3d.append(p3d_n)

def random_dis_euclid_syn(self, p3d_n, layer, layer_next):
    pass
def random_dis_euclid_uv_syn(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def random_dis_jump_uv_syn(self, p3d_n, layer, layer_next):
    p3d_t = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    self.p3d.append(p3d_t) 
def random_dis_uv_jump_syn(self, p3d_n, layer, layer_next):
    pass
def random_dis_normal_uv_syn(self, p3d_n, layer, layer_next):
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    # determine new point
    p3d_t = layer_next.map3dPointTo3d(layer_next, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d.append(p3d_t)
def random_dis_uv_normal_syn(self, p3d_n, layer, layer_next):
    pass

"""Topological mapping"""
def con_top(self, layer, layer_next, dis_func):
    p3d_n = layer.map3dPointTo3d(layer_next, self.p3d[-1])
    dis_func(self, p3d_n, layer, layer_next)
    return p3d_n

def top_dis_euclid(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def top_dis_euclid_uv(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def top_dis_jump_uv(self, p3d_n, layer, layer_next):
    p3d_t = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    self.p3d.append(p3d_t)
    self.p3d = self.p3d + layer_next.interpolateUVTrackIn3D(p3d_t, p3d_n)
    self.p3d.append(p3d_n)
def top_dis_uv_jump(self, p3d_n, layer, layer_next):
    p3d_t = layer.map3dPointTo3d(layer, p3d_n)
    self.p3d = self.p3d + layer.interpolateUVTrackIn3D(self.p3d[-1], p3d_t)
    self.p3d.append(p3d_n)
def top_dis_normal_uv(self, p3d_n, layer, layer_next):
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    p3d_t = layer_next.map3dPointTo3d(layer_next, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d.append(p3d_t)
    self.p3d = self.p3d + layer_next.interpolateUVTrackIn3D(p3d_t, p3d_n)
    self.p3d.append(p3d_n)
def top_dis_uv_normal(self, p3d_n, layer, layer_next):
    p, n, f = layer_next.closest_point_on_mesh(p3d_n)
    p3d_t = layer.map3dPointTo3d(layer, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d = self.p3d + layer.interpolateUVTrackIn3D(self.p3d[-1], p3d_t)
    self.p3d.append(p3d_t)
    self.p3d.append(p3d_n)

def top_dis_euclid_syn(self, p3d_n, layer, layer_next):
    pass
def top_dis_euclid_uv_syn(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def top_dis_jump_uv_syn(self, p3d_n, layer, layer_next):
    p3d_t = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    self.p3d.append(p3d_t)
def top_dis_uv_jump_syn(self, p3d_n, layer, layer_next):
    pass
def top_dis_normal_uv_syn(self, p3d_n, layer, layer_next):
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    # determine new point
    p3d_t = layer_next.map3dPointTo3d(layer_next, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d.append(p3d_t)
def top_dis_uv_normal_syn(self, p3d_n, layer, layer_next):
    pass

"""UV mapping"""
def con_uv(self, layer, layer_next, dis_func):
    p2d_t = layer.map3dPointToUV(self.p3d[-1])
    p3d_n = layer_next.mapUVPointTo3d([p2d_t])

    if p3d_n == []:
        raise MappingException()

    p3d_n = p3d_n[0]

    dis_func(self, p3d_n, layer, layer_next)
    return p3d_n

def uv_dis_euclid(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def uv_dis_euclid_uv(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def uv_dis_jump_uv(self, p3d_n, layer, layer_next):
    p3d_t = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    self.p3d.append(p3d_t)
    self.p3d = self.p3d + layer_next.interpolateUVTrackIn3D(p3d_t, p3d_n)
    self.p3d.append(p3d_n)
def uv_dis_uv_jump(self, p3d_n, layer, layer_next):
    p3d_t = layer.map3dPointTo3d(layer, p3d_n)
    self.p3d = self.p3d + layer.interpolateUVTrackIn3D(self.p3d[-1], p3d_t)
    self.p3d.append(p3d_n)
def uv_dis_normal_uv(self, p3d_n, layer, layer_next):
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    p3d_t = layer_next.map3dPointTo3d(layer_next, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d.append(p3d_t)
    self.p3d = self.p3d + layer_next.interpolateUVTrackIn3D(p3d_t, p3d_n)
    self.p3d.append(p3d_n)
def uv_dis_uv_normal(self, p3d_n, layer, layer_next):
    p, n, f = layer_next.closest_point_on_mesh(p3d_n)
    p3d_t = layer.map3dPointTo3d(layer, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d = self.p3d + layer.interpolateUVTrackIn3D(self.p3d[-1], p3d_t)
    self.p3d.append(p3d_t)
    self.p3d.append(p3d_n)
def uv_dis_euclid_syn(self, p3d_n, layer, layer_next):
    pass
def uv_dis_euclid_uv_syn(self, p3d_n, layer, layer_next):
    self.p3d.append(p3d_n)
def uv_dis_jump_uv_syn(self, p3d_n, layer, layer_next):
    p3d_t = layer_next.map3dPointTo3d(layer_next, self.p3d[-1])
    self.p3d.append(p3d_t)
def uv_dis_uv_jump_syn(self, p3d_n, layer, layer_next):
    pass
def uv_dis_normal_uv_syn(self, p3d_n, layer, layer_next):
    p, n, f = layer.closest_point_on_mesh(self.p3d[-1])
    # determine new point
    p3d_t = layer_next.map3dPointTo3d(layer_next, p, n)
    if p3d_t is None:
        raise MappingException()
    self.p3d.append(p3d_t)
def uv_dis_uv_normal_syn(self, p3d_n, layer, layer_next):
    pass

def con_mask3d(self, layer, layer_next, dis_func):
    if not checkPointInObject(layer_next, self.p3d[-1]):
        raise MappingException()
    else:
        p3d_n = self.p3d[-1]

    self.p3d.append(p3d_n)
    return p3d_n


connection_dict = {
    MAP_euclid: con_euclid,
    MAP_normal: con_normal,
    MAP_random: con_random,
    MAP_top: con_top,
    MAP_uv: con_uv,
    MAP_mask3D: con_mask3d
}

distance_dict = {
    MAP_euclid: {
        DIS_euclid:   euclid_dis_euclid,
        DIS_euclidUV: euclid_dis_euclid_uv,
        DIS_jumpUV:   euclid_dis_jump_uv,
        DIS_UVjump:   euclid_dis_uv_jump,
        DIS_normalUV: euclid_dis_normal_uv,
        DIS_UVnormal: euclid_dis_uv_normal 
    },
    MAP_normal: {
        DIS_euclid:   normal_dis_euclid,
        DIS_euclidUV: normal_dis_euclid_uv,
        DIS_jumpUV:   normal_dis_jump_uv,
        DIS_UVjump:   normal_dis_uv_jump,
        DIS_normalUV: normal_dis_normal_uv,
        DIS_UVnormal: normal_dis_uv_normal 
    },
    MAP_random: {
        DIS_euclid:   random_dis_euclid,
        DIS_euclidUV: random_dis_euclid_uv,
        DIS_jumpUV:   random_dis_jump_uv,
        DIS_UVjump:   random_dis_uv_jump,
        DIS_normalUV: random_dis_normal_uv,
        DIS_UVnormal: random_dis_uv_normal 
    },
    MAP_top: {
        DIS_euclid:   top_dis_euclid,
        DIS_euclidUV: top_dis_euclid_uv,
        DIS_jumpUV:   top_dis_jump_uv,
        DIS_UVjump:   top_dis_uv_jump,
        DIS_normalUV: top_dis_normal_uv,
        DIS_UVnormal: top_dis_uv_normal 
    },
    MAP_uv: {
        DIS_euclid:   uv_dis_euclid,
        DIS_euclidUV: uv_dis_euclid_uv,
        DIS_jumpUV:   uv_dis_jump_uv,
        DIS_UVjump:   uv_dis_uv_jump,
        DIS_normalUV: uv_dis_normal_uv,
        DIS_UVnormal: uv_dis_uv_normal 
    },
    MAP_mask3D: {
        DIS_euclid:   None,
        DIS_euclidUV: None,
        DIS_jumpUV:   None,
        DIS_UVjump:   None,
        DIS_normalUV: None,
        DIS_UVnormal: None 
    },
}

distance_dict_syn = {
    MAP_euclid: {
        DIS_euclid:   euclid_dis_euclid_syn,
        DIS_euclidUV: euclid_dis_euclid_uv_syn,
        DIS_jumpUV:   euclid_dis_jump_uv_syn,
        DIS_UVjump:   euclid_dis_uv_jump_syn,
        DIS_normalUV: euclid_dis_normal_uv_syn,
        DIS_UVnormal: euclid_dis_uv_normal_syn 
    },
    MAP_normal: {
        DIS_euclid:   normal_dis_euclid_syn,
        DIS_euclidUV: normal_dis_euclid_uv_syn,
        DIS_jumpUV:   normal_dis_jump_uv_syn,
        DIS_UVjump:   normal_dis_uv_jump_syn,
        DIS_normalUV: normal_dis_normal_uv_syn,
        DIS_UVnormal: normal_dis_uv_normal_syn 
    },
    MAP_random: {
        DIS_euclid:   random_dis_euclid_syn,
        DIS_euclidUV: random_dis_euclid_uv_syn,
        DIS_jumpUV:   random_dis_jump_uv_syn,
        DIS_UVjump:   random_dis_uv_jump_syn,
        DIS_normalUV: random_dis_normal_uv_syn,
        DIS_UVnormal: random_dis_uv_normal_syn 
    },
    MAP_top: {
        DIS_euclid:   top_dis_euclid_syn,
        DIS_euclidUV: top_dis_euclid_uv_syn,
        DIS_jumpUV:   top_dis_jump_uv_syn,
        DIS_UVjump:   top_dis_uv_jump_syn,
        DIS_normalUV: top_dis_normal_uv_syn,
        DIS_UVnormal: top_dis_uv_normal_syn 
    },
    MAP_uv: {
        DIS_euclid:   uv_dis_euclid_syn,
        DIS_euclidUV: uv_dis_euclid_uv_syn,
        DIS_jumpUV:   uv_dis_jump_uv_syn,
        DIS_UVjump:   uv_dis_uv_jump_syn,
        DIS_normalUV: uv_dis_normal_uv_syn,
        DIS_UVnormal: uv_dis_uv_normal_syn 
    },
    MAP_mask3D: {
        DIS_euclid:   None,
        DIS_euclidUV: None,
        DIS_jumpUV:   None,
        DIS_UVjump:   None,
        DIS_normalUV: None,
        DIS_UVnormal: None 
    },
}