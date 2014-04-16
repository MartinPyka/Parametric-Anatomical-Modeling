import code
import copy
import imp
import math
import random

import bpy
import mathutils
import numpy as np

from . import exporter
from . import config
from . import helper
from . import pam_vis


imp.reload(helper)
imp.reload(config)
# imp.reload(pam_vis)

DEBUG_LEVEL = 0
DEFAULT_MAXTRIALS = 50

pam_ng_list = []                # ng = neurongroup
pam_ng_dict = {}
pam_connection_counter = 0
pam_connection_indices = []
pam_connections = []
pam_connection_results = []


def computePoint(v1, v2, v3, v4, x1, x2):
    # computes an average point on the polygon depending on x1 and x2
    mv12_co = v1.co * x1 + v2.co * (1 - x1)
    mv34_co = v3.co * (1 - x1) + v4.co * x1
    mv_co = mv12_co * x2 + mv34_co * (1 - x2)

    return mv_co


def selectRandomPoint(object):
        # select a random polygon
        p_select = random.random() * object['area_sum']
        polygon = object.data.polygons[
            np.nonzero(np.array(object['area_cumsum']) > p_select)[0][0]]

        # define position on the polygon
        vert_inds = polygon.vertices[:]
        poi = computePoint(object.data.vertices[vert_inds[0]],
                           object.data.vertices[vert_inds[1]],
                           object.data.vertices[vert_inds[2]],
                           object.data.vertices[vert_inds[3]],
                           random.random(), random.random())

        p, n, f = object.closest_point_on_mesh(poi)

        return p, n, f


def computeUVScalingFactor(object):
    """computes the scaling factor between uv- and 3d-coordinates for a
    given object
    the return value is the factor that has to be multiplied with the
    uv-coordinates in order to have metrical relation
    """

    result = []

    for i in range(0, len(object.data.polygons)):
        uvs = [object.data.uv_layers.active.data[li] for li in object.data.polygons[i].loop_indices]

        rdist = (object.data.vertices[object.data.polygons[i].vertices[0]].co - object.data.vertices[object.data.polygons[i].vertices[1]].co).length
        mdist = (uvs[0].uv - uvs[1].uv).length
        result.append(rdist / mdist)

    # TODO (MP): compute scaling factor on the basis of all edges
    return np.mean(result), result


# TODO(SK): Quads into triangles (indices)
def map3dPointToUV(object, object_uv, point, normal=None):
    """Converts a given 3d-point into uv-coordinates,
    object for the 3d point and object_uv must have the same topology
    if normal is not None, the normal is used to detect the point on object, otherwise
    the closest_point_on_mesh operation is used
    """

    # if normal is None, we don't worry about orthogonal projections
    if normal is None:
        # get point, normal and face of closest point to a given point
        p, n, f = object.closest_point_on_mesh(point)
    else:
        p, n, f = object.ray_cast(point + normal * config.ray_fac, point - normal * config.ray_fac)
        # if no collision could be detected, return None
        if f == -1:
            return None

    # get the uv-coordinate of the first triangle of the polygon
    A = object.data.vertices[object.data.polygons[f].vertices[0]].co
    B = object.data.vertices[object.data.polygons[f].vertices[1]].co
    C = object.data.vertices[object.data.polygons[f].vertices[2]].co

    # and the uv-coordinates of the first triangle
    uvs = [object_uv.data.uv_layers.active.data[li] for li in object_uv.data.polygons[f].loop_indices]
    U = uvs[0].uv.to_3d()
    V = uvs[1].uv.to_3d()
    W = uvs[2].uv.to_3d()

    # convert 3d-coordinates of point p to uv-coordinates
    p_uv = mathutils.geometry.barycentric_transform(p, A, B, C, U, V, W)

    # if the point is not within the first triangle, we have to repeat the calculation
    # for the second triangle
    if mathutils.geometry.intersect_point_tri_2d(p_uv.to_2d(), uvs[0].uv, uvs[1].uv, uvs[2].uv) == 0:
        A = object.data.vertices[object.data.polygons[f].vertices[0]].co
        B = object.data.vertices[object.data.polygons[f].vertices[2]].co
        C = object.data.vertices[object.data.polygons[f].vertices[3]].co

        U = uvs[0].uv.to_3d()
        V = uvs[2].uv.to_3d()
        W = uvs[3].uv.to_3d()

        p_uv = mathutils.geometry.barycentric_transform(p, A, B, C, U, V, W)

    return p_uv.to_2d()


# TODO(SK): Quads into triangles (indices)
def mapUVPointTo3d(object_uv, uv_list):
    """Converts a given UV-coordinate into a 3d point,
    object for the 3d point and object_uv must have the same topology
    if normal is not None, the normal is used to detect the point on object, otherwise
    the closest_point_on_mesh operation is used
    """

    uv_polygons = []

    points_3d = [[] for j in range(len(uv_list))]
    to_find = [i for i in range(len(uv_list))]

    for p in uv_polygons:
        uvs = [object_uv.data.uv_layers.active.data[li] for li in p.loop_indices]
        for i in to_find:
            result = mathutils.geometry.intersect_point_tri_2d(uv_list[i],
                                                uvs[0].uv,
                                                uvs[1].uv,
                                                uvs[2].uv)
            if result == 1:
                U = uvs[0].uv.to_3d()
                V = uvs[1].uv.to_3d()
                W = uvs[2].uv.to_3d()
                A = object_uv.data.vertices[p.vertices[0]].co
                B = object_uv.data.vertices[p.vertices[1]].co
                C = object_uv.data.vertices[p.vertices[2]].co
                points_3d[i] = mathutils.geometry.barycentric_transform(uv_list[i].to_3d(), U, V, W, A, B, C)
                to_find.remove(i)
            else:
                result = mathutils.geometry.intersect_point_tri_2d(uv_list[i],
                                                    uvs[0].uv,
                                                    uvs[2].uv,
                                                    uvs[3].uv)
                if result == 1:
                    U = uvs[0].uv.to_3d()
                    V = uvs[2].uv.to_3d()
                    W = uvs[3].uv.to_3d()
                    A = object_uv.data.vertices[p.vertices[0]].co
                    B = object_uv.data.vertices[p.vertices[2]].co
                    C = object_uv.data.vertices[p.vertices[3]].co
                    points_3d[i] = mathutils.geometry.barycentric_transform(uv_list[i].to_3d(), U, V, W, A, B, C)
                    to_find.remove(i)
            if len(to_find) == 0:
                return points_3d

    for p in object_uv.data.polygons:
        uvs = [object_uv.data.uv_layers.active.data[li] for li in p.loop_indices]
        for i in to_find:
            result = mathutils.geometry.intersect_point_tri_2d(uv_list[i],
                                                uvs[0].uv,
                                                uvs[1].uv,
                                                uvs[2].uv)
            if result == 1:
                U = uvs[0].uv.to_3d()
                V = uvs[1].uv.to_3d()
                W = uvs[2].uv.to_3d()
                A = object_uv.data.vertices[p.vertices[0]].co
                B = object_uv.data.vertices[p.vertices[1]].co
                C = object_uv.data.vertices[p.vertices[2]].co
                points_3d[i] = mathutils.geometry.barycentric_transform(uv_list[i].to_3d(), U, V, W, A, B, C)
                to_find.remove(i)
                uv_polygons.append(p)
            else:
                result = mathutils.geometry.intersect_point_tri_2d(uv_list[i],
                                                    uvs[0].uv,
                                                    uvs[2].uv,
                                                    uvs[3].uv)
                if result == 1:
                    U = uvs[0].uv.to_3d()
                    V = uvs[2].uv.to_3d()
                    W = uvs[3].uv.to_3d()
                    A = object_uv.data.vertices[p.vertices[0]].co
                    B = object_uv.data.vertices[p.vertices[2]].co
                    C = object_uv.data.vertices[p.vertices[3]].co
                    points_3d[i] = mathutils.geometry.barycentric_transform(uv_list[i].to_3d(), U, V, W, A, B, C)
                    to_find.remove(i)
                    uv_polygons.append(p)
            if len(to_find) == 0:
                return points_3d

    points_3d = [p for p in points_3d if p != []]

    return points_3d


# TODO(MP): triangle check could be made more efficient
# TODO(MP): check the correct triangle order !!!
def map3dPointTo3d(o1, o2, point, normal=None):
    """maps a 3d-point on a given object on another object. Both objects must have the
    same topology
    """

    # if normal is None, we don't worry about orthogonal projections
    if normal is None:
        # get point, normal and face of closest point to a given point
        p, n, f = o1.closest_point_on_mesh(point)
    else:
        p, n, f = o1.ray_cast(point + normal * config.ray_fac, point - normal * config.ray_fac)
        # if no collision could be detected, return None
        if f == -1:
            return None

    # if o1 and o2 are identical, there is nothing more to do
    if (o1 == o2):
        return p

    # get the vertices of the first triangle of the polygon from both objects
    A1 = o1.data.vertices[o1.data.polygons[f].vertices[0]].co
    B1 = o1.data.vertices[o1.data.polygons[f].vertices[1]].co
    C1 = o1.data.vertices[o1.data.polygons[f].vertices[2]].co

    # project the point on a 2d-surface and check, whether we are in the right triangle
    t1 = mathutils.Vector()
    t2 = mathutils.Vector((1.0, 0.0, 0.0))
    t3 = mathutils.Vector((0.0, 1.0, 0.0))

    p_test = mathutils.geometry.barycentric_transform(p, A1, B1, C1, t1, t2, t3)

    # if the point is on the 2d-triangle, proceed with the real barycentric_transform
    if mathutils.geometry.intersect_point_tri_2d(p_test.to_2d(), t1.xy, t2.xy, t3.xy) == 1:
        A2 = o2.data.vertices[o2.data.polygons[f].vertices[0]].co
        B2 = o2.data.vertices[o2.data.polygons[f].vertices[1]].co
        C2 = o2.data.vertices[o2.data.polygons[f].vertices[2]].co

        # convert 3d-coordinates of the point
        p_new = mathutils.geometry.barycentric_transform(p, A1, B1, C1, A2, B2, C2)

    else:
        # use the other triangle
        A1 = o1.data.vertices[o1.data.polygons[f].vertices[0]].co
        B1 = o1.data.vertices[o1.data.polygons[f].vertices[2]].co
        C1 = o1.data.vertices[o1.data.polygons[f].vertices[3]].co

        A2 = o2.data.vertices[o2.data.polygons[f].vertices[0]].co
        B2 = o2.data.vertices[o2.data.polygons[f].vertices[2]].co
        C2 = o2.data.vertices[o2.data.polygons[f].vertices[3]].co

        # convert 3d-coordinates of the point
        p_new = mathutils.geometry.barycentric_transform(p, A1, B1, C1, A2, B2, C2)

    return p_new


# TODO(MP): Kernel definition must be equal across code fragments
# TODO(MP): Kernel functions can moved to separate module
def connfunc_gauss_post(uv, guv, *args):
    """Gauss-function for 2d
    u, v    : coordinates, to determine the function value
    vu, vv  : variance for both dimensionsj
    su, sv  : shift in u and v direction
    """
    vu = args[0][0]
    vv = args[0][1]
    su = args[0][2]
    sv = args[0][3]

    ruv = guv - uv  # compute relative position

    return math.exp(-((ruv[0] + su) ** 2 / (2 * vu ** 2) +
                    (ruv[1] + sv) ** 2 / (2 * vv ** 2)))


def connfunc_gauss_pre(u, v, *args):
    """Gauss-function for 2d
    u, v    : coordinates, to determine the function value
    vu, vv  : variance for both dimensions
    su, sv  : shift in u and v direction
    """

    vu = args[0][0]
    vv = args[0][1]
    su = args[0][2]
    sv = args[0][3]

    return [random.gauss(0, vu) + su, random.gauss(0, vv) + sv]


def connfunc_unity(u, v, *args):
    return 1


def computeConnectivityProbability(uv1, uv2, func, args):
    return func(uv1, uv2, args)


def interpolateUVTrackIn3D(p1_3d, p2_3d, layer):
    """ Creates a 3D-path along given 3d-coordinates p1_3d and p2_3d on layer """
    # get 2d-coordinates
    p1_2d = map3dPointToUV(layer, layer, p1_3d)
    p2_2d = map3dPointToUV(layer, layer, p2_3d)

    uv_p_2d = []

    for interp in range(1, config.INTERPOLATION_QUALITY):
        ip = interp / config.INTERPOLATION_QUALITY
        uv_p_2d.append(p2_2d * ip + p1_2d * (1 - ip))

    i_3d = mapUVPointTo3d(layer, uv_p_2d)

    return i_3d


def computeDistance_PreToSynapse(no_connection, pre_index):
    """ computes distance for a pre-synaptic neuron and a certain
    connection definition
    """
    layers = pam_connections[no_connection][0]
    neuronset1 = pam_connections[no_connection][1]
    slayer = pam_connections[no_connection][3]
    connections = pam_connections[no_connection][4]
    distances = pam_connections[no_connection][5]

    point = layers[0].particle_systems[neuronset1].particles[pre_index].location

    pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer + 1)],
                                             connections[0:slayer],
                                             distances[0:slayer],
                                             point)

    length = computePathLength(pre_p3d)

    return length, pre_p3d


def computePathLength(path):
    """ computes for an array of 3d-vectors their length in space """
    length = 0

    for p in range(1, len(path)):
        length = length + (path[p] - path[p - 1]).length

    return length


def computeMapping(layers, connections, distances, point):
    """based on a list of layers, connections-properties and distance-properties,
    this function returns the 3d-point, the 2d-uv-point and the distance from a given
    point on the first layer to the corresponding point on the last layer
    layers              : list of layers connecting the pre-synaptic layer with the synaptic layer
    connections         : list of values determining the type of layer-mapping
    distances           : list of values determining the calculation of the distances between layers
    point               : 3d vector for which the mapping should be calculated

    Return values
    -----------------
    p3d                 : list of 3d-vector of the neuron position on all layers until the last
                          last position before the synapse. Note, that this might be before the
                          synapse layer!!! This depends on the distance-property.
    p2d                 : 2d-vector of the neuron position on the UV map of the last layer
    d                   : distance between neuron position on the first layer and last position before
                          the synapse! This is not the distance to the p3d point! This is either the
                          distance to the 3d-position of the last but one layer or, in case
                          euclidean-uv-distance was used, the distance to the position of the last
                          layer determind by euclidean-distance. Functions, like computeConnectivity()
                          add the distance to the synapse to value d in order to retrieve
                          the complete distance from the pre- or post-synaptic neuron
                          to the synapse
    """

    p3d = [point]
    d = 0

    # go through all connection-elements
    for i in range(0, len(connections)):
        # print(i)
        # if euclidean mapping should be computed
        if connections[i] == config.MAP_euclid:
            # compute the point on the next intermediate layer
            p3d_n = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])

            # we are not on the synapse layer
            if (i < (len(connections) - 1)):

                if distances[i] == config.DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_jumpUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        return None, None, None
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_UVnormal:
                    p, n, f = layers[i + 1].closest_point_on_mesh(p3d_n)
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p, n)
                    if p3d_t is None:
                        return None, None, None

                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_t)
                    p3d.append(p3d_n)

            # or the last point before the synaptic layer
            else:
                # if distances[i] == config.DIS_euclid:
                #    do nothing
                if distances[i] == config.DIS_euclidUV:
                    p3d.append(p3d_n)
                # if distances[i] == config.DIS_jumpUV:
                #    do nothing
                elif distances[i] == config.DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    # determine new point
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        return None, None, None
                    p3d.append(p3d_t)
                # elif distances[i] == config.DIS_UVnormal:
                #    do nothing

        # if normal mapping should be computed
        elif connections[i] == config.MAP_normal:
            # compute normal on layer for the last point
            p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
            # determine new point
            p3d_n = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
            # if there is no intersection, abort
            if p3d_n is None:
                return None, None, None

            # we are not on the synapse layer
            if i < (len(connections) - 1):
                if distances[i] == config.DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == config.normalUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.UVnormal:
                    p3d.append(p3d_n)
            else:
                # if distances[i] == config.DIS_euclid:
                #   do nothing
                if distances[i] == config.DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                elif distances[i] == config.DIS_normalUV:
                    p3d.append(p3d_n)
                # elif distances[i] == config.UVnormal:
                #    do nothing

        # if random mapping should be used
        elif connections[i] == config.MAP_random:
            p3d_n, n, f = selectRandomPoint(layers[i + 1])

            # if this is not the synapse layer
            if (i < (len(connections) - 1)):
                if distances[i] == config.DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == config.normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == config.UVnormal:
                    p, n, f = layers[i + 1].closest_point_on_mesh(p3d_n)
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p, n)
                    if p3d_t is None:
                        return None, None, None

                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_t)
                    p3d.append(p3d_n)
            else:
                # if distances[i] == config.DIS_euclid:
                #   do nothing
                if distances[i] == config.DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                elif distances[i] == config.DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    # determine new point
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        return None, None, None
                    p3d.append(p3d_t)
                # elif distances[i] == config.UVnormal:
                #    do nothing

        # if both layers are topologically identical
        elif connections[i] == config.MAP_top:
            p3d_n = map3dPointTo3d(layers[i], layers[i + 1], p3d[-1])
            # if this is not the last layer, compute the topological mapping
            if i < (len(connections) - 1):
                if distances[i] == config.DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == config.normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == config.UVnormal:
                    p, n, f = layers[i + 1].closest_point_on_mesh(p3d_n)
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p, n)
                    if p3d_t is None:
                        return None, None, None

                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_t)
                    p3d.append(p3d_n)

            else:
                # if distances[i] == config.DIS_euclid:
                #   do nothing
                if distances[i] == config.DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == config.DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                elif distances[i] == config.DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    # determine new point
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        return None, None, None
                    p3d.append(p3d_t)
                # elif distances[i] == config.UVnormal:
                #    do nothing

        # for the synaptic layer, compute the uv-coordinates
        if i == (len(connections) - 1):
            p2d = map3dPointToUV(layers[i + 1], layers[i + 1], p3d_n)

    return p3d, p2d, computePathLength(p3d)


def computeDistanceToSynapse(ilayer, slayer, p_3d, s_2d, dis):
    """ computes the distance between the last 3d-point and the synapse
    ilayer      : last intermediate layer
    slayer      : synaptic layer
    p_3d        : last 3d-point
    s_2d        : uv-coordinates of the synapse
    dis         : distance calculation technique
    """

    if dis == config.DIS_euclid:
        i_3d = mapUVPointTo3d(slayer, [s_2d])
        if i_3d[0] == []:
            print("Need to exclude one connection")
            return -1, -1
        else:
            return (p_3d - i_3d[0]).length, i_3d

    elif dis == config.DIS_euclidUV:
        s_3d = mapUVPointTo3d(slayer, [s_2d])
        if s_3d is None:
            print("Need to exclude one connection")
            return -1, -1
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, s_3d[0], slayer)
        path.append(s_3d[0])
        return computePathLength(path), path

    elif dis == config.DIS_jumpUV:
        s_3d = mapUVPointTo3d(slayer, [s_2d])
        if s_3d is None:
            print("Need to exclude one connection")
            return -1, -1
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, s_3d[0], slayer)
        path.append(s_3d[0])
        return computePathLength(path), path

    elif dis == config.DIS_normalUV:
        s_3d = mapUVPointTo3d(slayer, [s_2d])
        if s_3d is None:
            print("Need to exclude one connection")
            return -1, -1
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, s_3d[0], slayer)
        path.append(s_3d[0])
        return computePathLength(path), path

    elif dis == config.DIS_UVnormal:
        s_3d = mapUVPointTo3d(slayer, [s_2d])
        if s_3d is None:
            print("Need to exclude one connection")
            return -1, -1
        p, n, f = slayers.closest_point_on_mesh(s_3d[0])
        t_3d = map3dPointTo3d(ilayers, ilayers, p, n)
        if t_3d is None:
            return -1, -1
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, t_3d, ilayers)
        path.append(t_3d)
        path.append(s_3d[0])
        return computePathLength(path), path


def addConnection(*args):
    global pam_connections

    pam_connections.append(args)

    # returns the future index of the connection
    return (len(pam_connections) - 1)

# TODO(SK): ??? closing brackets are switched

#    pam_connections.append(
#    {'layers': args[0],
#     'neuronset1': args[1],
#     'neuronset2': args[2],
#     'slayer': args[3],
#     'connections': args[4],
#     'distances': args[5],
#     'func_pre': args[6],
#     'args_pre': args[7],
#     'func_post': args[8],
#     'args_post': args[9],
#     'no_synapses': args[10] )
#     }


def computeAllConnections():
    global pam_connections
    global pam_connection_results

    for c in pam_connections:
        print(c[0][0].name + ' - ' + c[0][-1].name)

        result = computeConnectivity(*c)
        pam_connection_results.append(
            {
                'c': result[0],
                'd': result[1],
                's': result[2]
            }
        )
        print(" ")


def computeConnectivity(layers, neuronset1, neuronset2, slayer,
                        connections, distances,
                        func_pre, args_pre, func_post, args_post,
                        no_synapses):
    """ Computes for each pre-synaptic neuron no_synapses connections to post-synaptic neurons
    with the given parameters
    layers              : list of layers connecting a pre- with a post-synaptic layer
    neuronset1,
    neuronset2          : name of the neuronset (particle system) of the pre- and post-synaptic layer
    slayer              : index in layers for the synaptic layer
    connections         : list of values determining the type of layer-mapping
    distances           : list of values determining the calculation of the distances between layers
    func_pre, args_pre  : function of the pre-synaptic connectivity kernel, if func_pre is None
                          only the mapping position of the pre-synaptic neuron on the synaptic layer
                          is used
    func_post, args_post: same, as for func_pre and and args_pre, but now for the post-synaptic neurons
                          again, func_post can be None. Then a neuron is just assigned to the cell
                          of its corresponding position on the synapse layer
    no_synapses         : number of synapses for each pre-synaptic neuron
    """
    global pam_ng_list
    global pam_ng_dict
    global pam_connection_counter
    global pam_connection_indices

    # connection matrix
    conn = np.zeros((len(layers[0].particle_systems[neuronset1].particles), no_synapses)).astype(int)

    # distance matrix
    dist = np.zeros((len(layers[0].particle_systems[neuronset1].particles), no_synapses))

    # synapse mattrx (matrix, with the uv-coordinates of the synapses)
    syn = [[[] for j in range(no_synapses)] for i in range(len(layers[0].particle_systems[neuronset1].particles))]

    grid = helper.UVGrid(layers[slayer])

    # rescale arg-parameters
    args_pre = [i / layers[slayer]['uv_scaling'] for i in args_pre]
    args_post = [i / layers[slayer]['uv_scaling'] for i in args_post]

    print("Prepare Grid")

    grid.pre_kernel = func_post
    grid.pre_kernel_args = args_pre
    grid.compute_preMask()

    grid.post_kernel = func_post
    grid.post_kernel_args = args_post
    grid.compute_postMask()

    print("Compute Post-Mapping")

    # fill grid with post-neuron-links
    for i in range(0, len(layers[-1].particle_systems[neuronset2].particles)):
        post_p3d, post_p2d, post_d = computeMapping(layers[:(slayer - 1):-1],
                                                    connections[:(slayer - 1):-1],
                                                    distances[:(slayer - 1):-1],
                                                    layers[-1].particle_systems[neuronset2].particles[i].location)
        if post_p3d is None:
            continue

        grid.insert_postNeuron(i, post_p2d, post_p3d[-1], post_d)

#    namespace = globals().copy()
#    namespace.update(locals())
#    code.interact(local=namespace)

    print("Compute Pre-Mapping")
    num_particles = len(layers[0].particle_systems[neuronset1].particles)
    for i in range(0, num_particles):
        pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[i].location)

        print(str(round((i / num_particles) * 10000) / 100) + '%')
        if pre_p3d is None:
            continue

        post_neurons = grid.select_random(pre_p2d, no_synapses)

        if (len(post_neurons) == 0):
            for c in conn[i]:
                c = -1
            continue

        for j, post_neuron in enumerate(post_neurons):
            distance_pre, _ = computeDistanceToSynapse(
                layers[slayer - 1], layers[slayer], pre_p3d[-1], post_neuron[1], distances[slayer - 1])
            if distance_pre >= 0:
                distance_post, _ = computeDistanceToSynapse(
                    layers[slayer + 1], layers[slayer], post_neuron[0][2], post_neuron[1], distances[slayer])
                if distance_post >= 0:
                    conn[i, j] = post_neuron[0][0]      # the index of the post-neuron
                    dist[i, j] = pre_d + distance_pre + distance_post + post_neuron[0][3]      # the distance of the post-neuron
                    syn[i][j] = post_neuron[1]
                else:
                    conn[i, j] = -1
            else:
                conn[i, j] = -1

        for rest in range(j + 1, no_synapses):
            conn[i, j] = -1

    pam_connection_indices.append(
        [
            pam_connection_counter,
            pam_ng_dict[layers[0].name][neuronset1],
            pam_ng_dict[layers[-1].name][neuronset2]
        ]
    )
    pam_connection_counter += 1

    return conn, dist, syn, grid


def computeConnectivityAll(layers, neuronset1, neuronset2, slayer, connections, distances, func, args):
    """computes the connectivity probability between all neurons of both neuronsets
    on a synaptic layer
    layers              : list of layers connecting a pre- with a post-synaptic layer
    neuronset1,
    neuronset2          : name of the neuronset (particle system) of the pre- and post-synaptic layer
    slayer              : index in layers for the synaptic layer
    connections         : list of values determining the type of layer-mapping
    distances           : list of values determining the calculation of the distances between layers
    func                : function of the connectivity kernel
    args                : argument list for the connectivity kernel
    """

    # connection matrix
    conn = np.zeros((len(layers[0].particle_systems[neuronset1].particles),
                     len(layers[-1].particle_systems[neuronset2].particles)))

    # distance matrix
    dist = np.zeros((len(layers[0].particle_systems[neuronset1].particles),
                     len(layers[-1].particle_systems[neuronset2].particles)))

    for i in range(0, len(layers[0].particle_systems[neuronset1].particles)):
        # compute position, uv-coordinates and distance for the pre-synaptic neuron
        pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[i].location)
        if pre_p3d is None:
            continue

        for j in range(0, len(layers[-1].particle_systems[neuronset2].particles)):
            # compute position, uv-coordinates and distance for the post-synaptic neuron
            post_p3d, post_p2d, post_d = computeMapping(layers[:(slayer - 1):-1],
                                                        connections[:(slayer - 1):-1],
                                                        distances[:(slayer - 1):-1],
                                                        layers[-1].particle_systems[neuronset2].particles[j].location)

            if post_p3d is None:
                continue

            # determine connectivity probabiltiy and distance values
            conn[i, j] = computeConnectivityProbability(pre_p2d * layers[slayer]['uv_scaling'], post_p2d * layers[slayer]['uv_scaling'], func, args)
            # for euclidean distance
            if distances[slayer - 1] == 0:
                dist[i, j] = pre_d + post_d + (post_p3d[-1] - pre_p3d[-2]).length
            # for normal-uv-distance
            elif distances[slayer - 1] == 1:
                dist[i, j] = pre_d + post_d + (post_p2d - pre_p2d).length * layers[slayer]['uv_scaling']
            # for euclidean-uv-distances
            elif distances[slayer - 1] == 2:
                dist[i, j] = pre_d + post_d + (post_p2d - pre_p2d).length * layers[slayer]['uv_scaling']

    return conn, dist


def printConnections():
    """ Print all connection pairs """
    for i, c in enumerate(pam_connection_indices):
        print(i, pam_ng_list[c[1]][0] + ' - ' +
              pam_ng_list[c[2]][0])


def computeDistance(layer1, layer2, neuronset1, neuronset2, commonl, conn_matrix):
    """ measures the distance between neurons on the same layer according to the connectivity
    matrix
    layer1
    layer2      : layer of pre- and post-synaptic neurons
    neuronset1,
    neuronset2  : name of the neuronset (particlesystem)
    commonl     : layer, on which the distances should be measured
    conn_matrix : connectivity matrix that determines, which distances should be measured

    result      : matrix of the same structure, like conn_matrix, but with distances
    """
    positions1 = []     # list of uv-positions for the first group
    positions2 = []     # list of uv-positions for the second group
    for p in layer1.particle_systems[neuronset1].particles:
        p2d = map3dPointToUV(commonl, commonl, p.location)
        positions1.append(p2d)

    for p in layer2.particle_systems[neuronset2].particles:
        p2d = map3dPointToUV(commonl, commonl, p.location)
        positions2.append(p2d)

    result = np.zeros(conn_matrix.shape)
    for i in range(0, len(conn_matrix)):
        for j in range(0, len(conn_matrix[i])):
            result[i, j] = (positions2[conn_matrix[i][j]] - positions1[i]).length * commonl['uv_scaling']

    return result, positions1, positions2


def measureUVs(objects):
    """ Returns the ratio between real and UV-distance for all edges for all objects in
    objects

    objects             : list of objects to compute uv-data for

    Returns:
        uv_data         : list of ratio-vectors
        layer_names     : name of the object
    """
    uv_data = []
    layer_names = []
    for o in objects:
        if o.type == 'MESH':
            if len(o.data.uv_layers) > 0:
                uv_data.append(computeUVScalingFactor(o)[1])
                layer_names.append(o.name)

    return uv_data, layer_names


def initializeUVs():
    """ compute the UV scaling factor for all layers that have UV-maps """
    for o in bpy.data.objects:
        if o.type == 'MESH':
            if len(o.data.uv_layers) > 0:
                o['uv_scaling'] = computeUVScalingFactor(o)[0]

            ''' area size of each polygon '''
            p_areas = []

            ''' collect area values for all polygons '''
            for p in o.data.polygons:
                p_areas.append(p.area)

            # convert everything to numpy
            p_areas = np.array(p_areas)
            p_cumsum = p_areas.cumsum()     # compute the cumulative sum
            p_sum = p_areas.sum()           # compute the sum of all areas
            o['area_cumsum'] = p_cumsum
            o['area_sum'] = p_sum


def returnNeuronGroups():
    """ returns a list of neural groups (particle-systems) for the whole model.
    This is used for the NEST import to determine, which neural groups should be
    connected
    """
    r_list = []
    r_dict = {}
    counter = 0
    for o in bpy.data.objects:
        for p in o.particle_systems:
            r_list.append([o.name, p.name, p.settings.count])
            if r_dict.get(o.name) is None:
                r_dict[o.name] = {}
            r_dict[o.name][p.name] = counter
            counter += 1
    return r_list, r_dict


def initialize3D():
    """prepares all necessary steps for the computation of connections"""
    global pam_ng_list
    global pam_ng_dict
    global pam_connection_counter
    global pam_connection_indices

    print("Initialize 3D settings")
    print("- Compute UV-scaling factor")
    initializeUVs()             # compute the uv-scaling factor

    print(" -Collect all neuron groups")
    pam_ng_list, pam_ng_dict = returnNeuronGroups()

    Reset()

    print("End of Initialization")
    print("============================")


def Reset():
    """ Resets the most important variables without calculating everything from
    scratch """

    pam_ng_list = []                # ng = neurongroup
    pam_ng_dict = {}
    pam_connection_counter = 0
    pam_connection_indices = []
    pam_connections = []
    pam_connection_results = []


def test():
    """ Just a routine to perform some tests """
    # get all important layers
    dg = bpy.data.objects['DG_sg']
    ca3 = bpy.data.objects['CA3_sp']
    ca1 = bpy.data.objects['CA1_sp']
    al_dg = bpy.data.objects['DG_sg_axons_all']
    al_ca3 = bpy.data.objects['CA3_sp_axons_all']

    # get all important neuron groups
    ca3_neurons = 'CA3_Pyramidal'
    ca1_neurons = 'CA1_Pyramidal'

    # number of neurons per layer
    n_dg = 1200000
    n_ca3 = 250000
    n_ca1 = 390000

    # number of outgoing connectionso
    s_ca3_ca3 = 60000
    s_ca3_ca1 = 85800

    f = 0.001     # factor for the neuron numbers
    # adjust the number of neurons per layer
    ca3.particle_systems[ca3_neurons].settings.count = int(n_ca3 * f)
    ca1.particle_systems[ca1_neurons].settings.count = int(n_ca3 * f)

    pam_vis.visualizeClean()
    initialize3D()

    ca3_params_post = [0.3, 0.3, 0.0, 0.00]
    ca3_params_pre = [10., 0.2, 0.0, 0.00]
    ca1_params_post = ca3_params_post

    c_ca3_ca3, d_ca3_ca3, s_ca3_ca3, grid = computeConnectivity(
        [ca3, al_ca3, ca3],                      # layers involved in the connection
        ca3_neurons, ca3_neurons,       # neuronsets involved
        1,                                      # synaptic layer
        [config.MAP_normal, config.MAP_normal],                                 # connection mapping
        [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
        connfunc_gauss_pre, ca3_params_pre, connfunc_gauss_post, ca3_params_post,   # kernel function plus parameters
        int(s_ca3_ca3 * f)
    )                      # number of synapses for each  pre-synaptic neuron

    # namespace = globals().copy()
    # namespace.update(locals())
    # code.interact(local=namespace)

    c_ca3_ca1 = []
    d_ca3_ca1 = []
    s_ca3_ca1 = []
    grid = []
#    c_ca3_ca1, d_ca3_ca1, s_ca3_ca1, grid = computeConnectivity(
#        [ca3, al_ca3, ca1],                      # layers involved in the connection
#        ca3_neurons, ca1_neurons,      # neuronsets involved
#        1,                                      # synaptic layer
#        [config.MAP_normal, config.MAP_normal],                                 # connection mapping
#        [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
#        connfunc_gauss_pre, ca3_params_pre, connfunc_gauss_post, ca1_params_post,   # kernel function plus parameters
#        int(s_ca3_ca1 * f)
#    )                      # number of synapses for each  pre-synaptic neuron

    particle = 40

    pam_vis.setCursor(ca3.particle_systems[ca3_neurons].particles[particle].location)

    pam_vis.visualizePostNeurons(ca3, ca3_neurons, c_ca3_ca3[particle])
    # pam_vis.visualizePostNeurons(ca1, ca1_neurons, c_ca3_ca1[particle])

    pam_vis.visualizeConnectionsForNeuron(
        [ca3, al_ca3, ca3],                      # layers involved in the connection
        ca3_neurons, ca3_neurons,      # neuronsets involved
        1,                                      # synaptic layer
        [config.MAP_normal, config.MAP_normal],                                 # connection mapping
        [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
        particle,
        c_ca3_ca3[particle], s_ca3_ca3[particle]
    )

#    pam_vis.visualizeConnectionsForNeuron([ca3, al_ca3, ca1],                      # layers involved in the connection
#                                     ca3_neurons, ca1_neurons,       # neuronsets involved
#                                     1,                                      # synaptic layer
#                                     [config.MAP_normal, config.MAP_normal],                                 # connection mapping
#                                     [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
#                                     particle,
#                                     c_ca3_ca1[particle],
#                                     s_ca3_ca1[particle])

    return grid, c_ca3_ca3, d_ca3_ca3, s_ca3_ca3, c_ca3_ca1, d_ca3_ca1, s_ca3_ca1


def hippotest():
    """ A routine to test the functionality on a hippocampus-like shape """
    dg = bpy.data.objects['DG_sg']
    ca3 = bpy.data.objects['CA3_sp']
    ca1 = bpy.data.objects['CA1_sp']
    al_dg = bpy.data.objects['DG_sg_axons_all']
    al_ca3 = bpy.data.objects['CA3_sp_axons_all']

    # preparatory steps are done in initialize3D (e.g. calculating the uv-scaling-factor for all
    # meshs with uv-data.
    print('Initialize data')
    initialize3D()

    # connect ca3 with ca3 using an intermediate layer al_ca3. first relationship is topological,
    # second one is euclidian
    # use a gauss-function with given variance and shifting parameters to determine the connectivity

    params = [10., 1., -5., 0.00]

    print('Compute Connectivity for ca3 to ca1')
    c_ca3_ca3, d_ca3_ca3 = computeConnectivityAll([ca3, al_ca3, ca3],                      # layers involved in the connection
                                                  'CA3_Pyramidal', 'CA3_Pyramidal',       # neuronsets involved
                                                  1,                                      # synaptic layer
                                                  [config.MAP_top, config.MAP_euclid],                                 # connection mapping
                                                  [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
                                                  connfunc_gauss_post, params)   # kernel function plus parameters

    print('Compute Connectivity for ca3 to ca1')
    c_ca3_ca1, d_ca3_ca1 = computeConnectivityAll(
        [ca3, al_ca3, ca1],                      # layers involved in the connection
        'CA3_Pyramidal', 'CA1_Pyramidal',       # neuronsets involved
        1,                                      # synaptic layer
        [config.MAP_top, config.MAP_euclid],                                 # connection mapping
        [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
        connfunc_gauss_post, params
    )   # kernel function plus parameters

    # c_ca3_ca1 = computeConnectivity(ca3, 'CA3_Pyramidal', ca1, 'CA1_Pyramidal', al_ca3, 1, 0, connfunc_gauss, [3.0, 0.3, 2.3, 0.00])

    # the rest is just for visualization
    pam_vis.visualizeClean()

    particle = 20

    pam_vis.setCursor(ca3.particle_systems['CA3_Pyramidal'].particles[particle].location)

    pam_vis.visualizePostNeurons(ca3, 'CA3_Pyramidal', c_ca3_ca3[particle])
    pam_vis.visualizePostNeurons(ca1, 'CA1_Pyramidal', c_ca3_ca1[particle])

#    p3, p2, d = computeMapping([ca3, al_ca3],
#                               [config.MAP_top],
#                               [config.DIS_normalUV],
#                               ca3.particle_systems['CA3_Pyramidal'].particles[particle].location)
#    print(p3)
#    if (p3 != None):
#        pam_vis.visualizePath(p3)


def subiculumtest():
    ca1 = bpy.data.objects['CA1_sp']
    al_ca1 = bpy.data.objects['CA1_sp_axons_all']
    sub = bpy.data.objects['Subiculum']

    print('Initialize data')
    initialize3D()

    params = [0.5, 3., 0., 0.]

    c_ca1_sub, d_ca1_sub = computeConnectivityAll([ca1, al_ca1, sub],                      # layers involved in the connection
                                                  'CA1_Pyramidal', 'CA1_Pyramidal',       # neuronsets involved
                                                  1,                                      # synaptic layer
                                                  [1, 0],                                 # connection mapping
                                                  [1, 0],                                 # distance calculation
                                                  connfunc_gauss, params)   # kernel function plus parameters

    pam_vis.visualizeClean()

    particle = 44

    pam_vis.setCursor(ca1.particle_systems['CA1_Pyramidal'].particles[particle].location)

    pam_vis.visualizePostNeurons(ca1, 'CA1_Pyramidal', c_ca1_sub[particle])


if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # Main Code:
    # Here the connectivity between two layers using an intermediate layer
    # -------------------------------------------------------------------------

    test()
    # hippotest()
    # subiculumtest()

    # t201 = bpy.data.objects['t2.001']
    # grid = helper.UVGrid(t201)
    # grid.kernel = connfunc_gauss_post
    # grid.compute_kernel(0, 1, mathutils.Vector((0.0, 0.0)), [0.1, 0.1, 0., 0.])
    # print(grid._weights[0][0])
    # grid.compute_kernel(1, 1, mathutils.Vector((0.0, 0.0)), [0.1, 0.1, 0., 0.])
    # print(grid._weights[0][0])
