# TODO(SK): missing module docstring

import logging
import random

import bpy
import mathutils
import numpy

from . import constants
from . import grid
from . import model

logger = logging.getLogger(__package__)

# key-values for the mapping-procedure
MAP_euclid = 0
MAP_normal = 1
MAP_random = 2
MAP_top = 3
MAP_uv = 4

DIS_euclid = 0
DIS_euclidUV = 1
DIS_jumpUV = 2
DIS_UVjump = 3
DIS_normalUV = 4
DIS_UVnormal = 5


# TODO(SK): missing docstring
def computePoint(v1, v2, v3, v4, x1, x2):
    # computes an average point on the polygon depending on x1 and x2
    mv12_co = v1.co * x1 + v2.co * (1 - x1)
    mv34_co = v3.co * (1 - x1) + v4.co * x1
    mv_co = mv12_co * x2 + mv34_co * (1 - x2)

    return mv_co


# TODO(SK): missing docstring
def selectRandomPoint(obj):
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


def computeUVScalingFactor(obj):
    """computes the scaling factor between uv- and 3d-coordinates for a
    given object
    the return value is the factor that has to be multiplied with the
    uv-coordinates in order to have metrical relation
    """

    result = []

    for i in range(len(obj.data.polygons)):
        uvs = [obj.data.uv_layers.active.data[li] for li in obj.data.polygons[i].loop_indices]

        rdist = (obj.data.vertices[obj.data.polygons[i].vertices[0]].co - obj.data.vertices[obj.data.polygons[i].vertices[1]].co).length
        mdist = (uvs[0].uv - uvs[1].uv).length
        result.append(rdist / mdist)

    # TODO (MP): compute scaling factor on the basis of all edges
    return numpy.mean(result), result


# TODO(SK): Quads into triangles (indices)
def map3dPointToUV(obj, obj_uv, point, normal=None):
    """Converts a given 3d-point into uv-coordinates,
    obj for the 3d point and obj_uv must have the same topology
    if normal is not None, the normal is used to detect the point on obj, otherwise
    the closest_point_on_mesh operation is used
    """

    if normal:
        normal_scaled = normal * constants.RAY_FAC
        p, n, f = obj.ray_cast(point + normal_scaled, point - normal_)
        # if no collision could be detected, return None
        if f == -1:
            return None
    else:
        # get point, normal and face of closest point to a given point
        p, n, f = obj.closest_point_on_mesh(point)

    # get the uv-coordinate of the first triangle of the polygon
    A = obj.data.vertices[obj.data.polygons[f].vertices[0]].co
    B = obj.data.vertices[obj.data.polygons[f].vertices[1]].co
    C = obj.data.vertices[obj.data.polygons[f].vertices[2]].co

    # and the uv-coordinates of the first triangle
    uvs = [obj_uv.data.uv_layers.active.data[li] for li in obj_uv.data.polygons[f].loop_indices]
    U = uvs[0].uv.to_3d()
    V = uvs[1].uv.to_3d()
    W = uvs[2].uv.to_3d()

    # convert 3d-coordinates of point p to uv-coordinates
    p_uv = mathutils.geometry.barycentric_transform(p, A, B, C, U, V, W)

    # if the point is not within the first triangle, we have to repeat the calculation
    # for the second triangle
    if (mathutils.geometry.intersect_point_tri_2d(p_uv.to_2d(), uvs[0].uv, uvs[1].uv, uvs[2].uv) == 0) & (len(uvs) == 4):
        A = obj.data.vertices[obj.data.polygons[f].vertices[0]].co
        B = obj.data.vertices[obj.data.polygons[f].vertices[2]].co
        C = obj.data.vertices[obj.data.polygons[f].vertices[3]].co

        U = uvs[0].uv.to_3d()
        V = uvs[2].uv.to_3d()
        W = uvs[3].uv.to_3d()

        p_uv = mathutils.geometry.barycentric_transform(p, A, B, C, U, V, W)

    return p_uv.to_2d()


# TODO(SK): Quads into triangles (indices)
def mapUVPointTo3d(obj_uv, uv_list, cleanup=True):
    """ Converts a list of uv-points into 3d. This function is mostly
    used by interpolateUVTrackIn3D. Note, that therefore, not all points
    can and have to be converted to 3d points. The return list can therefore
    have less points than the uv-list. This cleanup can be deactivated
    by setting cleanup = False. Then, the return-list may contain
    some [] elements.
    """

    uv_polygons = []

    uv_list_range_container = range(len(uv_list))

    points_3d = [[] for _ in uv_list_range_container]
    unseen = [i for i in uv_list_range_container]

    for p in obj_uv.data.polygons:
        uvs = [obj_uv.data.uv_layers.active.data[li] for li in p.loop_indices]

        source_0 = uvs[0].uv.to_3d()
        source_1 = uvs[1].uv.to_3d()
        source_2 = uvs[2].uv.to_3d()
        source_3 = uvs[3].uv.to_3d()
        vertex_0 = obj_uv.data.vertices[p.vertices[0]].co
        vertex_1 = obj_uv.data.vertices[p.vertices[1]].co
        vertex_2 = obj_uv.data.vertices[p.vertices[2]].co
        vertex_3 = obj_uv.data.vertices[p.vertices[3]].co

        for i in list(unseen):
            point = uv_list[i].to_3d()

            result = mathutils.geometry.intersect_point_tri_2d(
                uv_list[i],
                uvs[0].uv,
                uvs[1].uv,
                uvs[2].uv
            )

            if (result != 0):
                points_3d[i] = mathutils.geometry.barycentric_transform(
                    point,
                    source_0,
                    source_1,
                    source_2,
                    vertex_0,
                    vertex_1,
                    vertex_2
                )
                uv_polygons.append(p)
                unseen.remove(i)

            else:
                result = mathutils.geometry.intersect_point_tri_2d(
                    uv_list[i],
                    uvs[0].uv,
                    uvs[2].uv,
                    uvs[3].uv
                )
                if (result != 0):
                    points_3d[i] = mathutils.geometry.barycentric_transform(
                        point,
                        source_0,
                        source_2,
                        source_3,
                        vertex_0,
                        vertex_2,
                        vertex_3
                    )

                    uv_polygons.append(p)
                    unseen.remove(i)

            if len(unseen) == 0:
                return points_3d

    if cleanup:
        points_3d = [p for p in points_3d if p]

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
        p, n, f = o1.ray_cast(point + normal * constants.RAY_FAC, point - normal * constants.RAY_FAC)
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


def map3dPointToParticle(obj, particle_system, location):
    """Determines based on a 3d-point location (e.g. given by the cursor
    position) the index of the closest particle on an object
    """

    index = -1
    distance = float("inf")
    for (i, p) in enumerate(obj.particle_systems[particle_system].particles):
        if (p.location - location).length < distance:
            distance = (p.location - location).length
            index = i

    return index


def maskParticle(p_layer, p_index, mask_layer, distance=0.2):
    """ Returns all particle-indices of particle_layer that have a smaller
    distance than the distance-argument to mask_layer
    p_layer         : object that contains the particles
    p_index         : index of particle-system
    mask_layer      : object that serves as mask
    distance        : distance threshold
    """
    result = []
    for i, p in enumerate(p_layer.particle_systems[p_index].particles):
        l, n, f = mask_layer.closest_point_on_mesh(p.location)
        if (p.location - l).length < distance:
            result.append(i)
    return result


def distanceToMask(p_layer, p_index, particle_index, mask_layer):
    """ Returns the distance for a particle to a mask_layer
    p_layer         : object with particle-system
    p_index         : index of particle-system
    particle_index  : index of particle
    mask_layer      : object that serves as mask
    """
    p = p_layer.particle_systems[p_index].particles[particle_index]
    l, n, f = mask_layer.closest_point_on_mesh(p.location)
    return (p.location - l).length


# TODO(SK): missing docstring
def computeConnectivityProbability(uv1, uv2, func, args):
    return func(uv1, uv2, args)


def interpolateUVTrackIn3D(p1_3d, p2_3d, layer):
    """Creates a 3D-path along given 3d-coordinates p1_3d and p2_3d on layer"""
    # get 2d-coordinates
    p1_2d = map3dPointToUV(layer, layer, p1_3d)
    p2_2d = map3dPointToUV(layer, layer, p2_3d)

    uv_p_2d = []

    for step in range(1, constants.INTERPOLATION_QUALITY + 1):
        interpolation = step / (constants.INTERPOLATION_QUALITY)
        uv_p_2d.append(p2_2d * interpolation + p1_2d * (1 - interpolation))

    ip_3d = mapUVPointTo3d(layer, uv_p_2d)

    return ip_3d


def computeDistance_PreToSynapse(no_connection, pre_index):
    """ computes distance for a pre-synaptic neuron and a certain
    connection definition
    """
    layers = model.CONNECTIONS[no_connection][0]
    neuronset1 = model.CONNECTIONS[no_connection][1]
    slayer = model.CONNECTIONS[no_connection][3]
    connections = model.CONNECTIONS[no_connection][4]
    distances = model.CONNECTIONS[no_connection][5]

    point = layers[0].particle_systems[neuronset1].particles[pre_index].location

    pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer + 1)],
                                             connections[0:slayer],
                                             distances[0:slayer],
                                             point)

    path_length = compute_path_length(pre_p3d)

    return path_length, pre_p3d


def compute_path_length(path):
    """ computes for an array of 3d-vectors their length in space """
    return sum([(path[i] - path[i - 1]).length for i in range(1, len(path))])


def sortNeuronsToUV(layer, neuronset, u_or_v):
    """Sorts particles according to their position on the u
    or v axis and returns the permutation indices

    layer       : the layers were the neurons are
    neuronset   : name or number of the neuronset (particle system)
    u_or_v      : 'u' means sort for u
                  'v' means sort for v
    """

    if u_or_v == 'u':
        index = 0
    elif u_or_v == 'v':
        index = 1
    else:
        raise Exception("u_or_v must be either 'u' or 'v' ")

    # get all particle positions
    p3d = [i.location for i in layer.particle_systems[neuronset].particles]
    # convert them to 2d and select just the u or v coordinate
    p2d = [map3dPointToUV(layer, layer, p)[index] for p in p3d]

    # return permutation of a sorted list (ascending)
    return numpy.argsort(p2d)


def computeMapping(layers, connections, distances, point, debug=False):
    """based on a list of layers, connections-properties and distance-properties,
    this function returns the 3d-point, the 2d-uv-point and the distance from a given
    point on the first layer to the corresponding point on the last layer
    layers              : list of layers connecting the pre-synaptic layer with the synaptic layer
    connections         : list of values determining the type of layer-mapping
    distances           : list of values determining the calculation of the distances between layers
    point               : 3d vector for which the mapping should be calculated
    debug               : if true, the function returns a list of layers that it was able
                          to pass. Helps to debug the mapping-definitions in order to figure
                          our where exactly the mapping stops

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
        if connections[i] == MAP_euclid:
            # compute the point on the next intermediate layer
            p3d_n = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])

            # we are not on the synapse layer
            if (i < (len(connections) - 1)):

                if distances[i] == DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVjump:
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p3d_n)
                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVnormal:
                    p, n, f = layers[i + 1].closest_point_on_mesh(p3d_n)
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None

                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_t)
                    p3d.append(p3d_n)

            # or the last point before the synaptic layer
            else:
                # if distances[i] == DIS_euclid:
                #    do nothing
                if distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d.append(p3d_n)
                # elif distances[i] = DIS_UVjump:
                #    do nothing
                elif distances[i] == DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    # determine new point
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None
                    p3d.append(p3d_t)
                # elif distances[i] == DIS_UVnormal:
                #    do nothing

        # if normal mapping should be computed
        elif connections[i] == MAP_normal:
            # compute normal on layer for the last point
            p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
            # determine new point
            p3d_n = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
            # if there is no intersection, abort
            if p3d_n is None:
                if not debug:
                    return None, None, None
                else:
                    return p3d, i, None

            # we are not on the synapse layer
            if i < (len(connections) - 1):
                if distances[i] == DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVjump:
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p3d_n)
                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_normalUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVnormal:
                    p3d.append(p3d_n)
            else:
                # if distances[i] == DIS_euclid:
                #   do nothing
                if distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                # elif distances[i] == DIS_UVjump:
                #    do nothing
                elif distances[i] == DIS_normalUV:
                    p3d.append(p3d_n)
                # elif distances[i] == UVnormal:
                #    do nothing

        # if random mapping should be used
        elif connections[i] == MAP_random:
            p3d_n, n, f = selectRandomPoint(layers[i + 1])

            # if this is not the synapse layer
            if (i < (len(connections) - 1)):
                if distances[i] == DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVjump:
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p3d_n)
                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVnormal:
                    p, n, f = layers[i + 1].closest_point_on_mesh(p3d_n)
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None

                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_t)
                    p3d.append(p3d_n)
            else:
                # if distances[i] == DIS_euclid:
                #   do nothing
                if distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                # elif distances[i] == DIS_UVjump:
                #    do nothing
                elif distances[i] == DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    # determine new point
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None
                    p3d.append(p3d_t)
                # elif distances[i] == UVnormal:
                #    do nothing

        # if both layers are topologically identical
        elif connections[i] == MAP_top:
            p3d_n = map3dPointTo3d(layers[i], layers[i + 1], p3d[-1])

            # if this is not the last layer, compute the topological mapping
            if i < (len(connections) - 1):
                if distances[i] == DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVjump:
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p3d_n)
                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVnormal:
                    p, n, f = layers[i + 1].closest_point_on_mesh(p3d_n)
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None

                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_t)
                    p3d.append(p3d_n)

            else:
                # if distances[i] == DIS_euclid:
                #   do nothing
                if distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                # elif distances[i] == DIS_UVjump:
                #    do nothing
                elif distances[i] == DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    # determine new point
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None
                    p3d.append(p3d_t)
                # elif distances[i] == UVnormal:
                #    do nothing

        # map via UV overlap
        elif connections[i] == MAP_uv:

            p2d_t = map3dPointToUV(layers[i], layers[i], p3d[-1])
            p3d_n = mapUVPointTo3d(layers[i + 1], [p2d_t])

            if p3d_n == []:
                if not debug:
                    return None, None, None
                else:
                    return p3d, i, None

            p3d_n = p3d_n[0]

            # if this is not the last layer, compute the topological mapping
            if i < (len(connections) - 1):
                if distances[i] == DIS_euclid:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVjump:
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p3d_n)
                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None
                    p3d.append(p3d_t)
                    p3d = p3d + interpolateUVTrackIn3D(p3d_t, p3d_n, layers[i + 1])
                    p3d.append(p3d_n)
                elif distances[i] == DIS_UVnormal:
                    p, n, f = layers[i + 1].closest_point_on_mesh(p3d_n)
                    p3d_t = map3dPointTo3d(layers[i], layers[i], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None

                    p3d = p3d + interpolateUVTrackIn3D(p3d[-1], p3d_t, layers[i])
                    p3d.append(p3d_t)
                    p3d.append(p3d_n)

            else:
                # if distances[i] == DIS_euclid:
                #   do nothing
                if distances[i] == DIS_euclidUV:
                    p3d.append(p3d_n)
                elif distances[i] == DIS_jumpUV:
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p3d[-1])
                    p3d.append(p3d_t)
                # elif distances[i] == DIS_UVjump:
                #    do nothing
                elif distances[i] == DIS_normalUV:
                    p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
                    # determine new point
                    p3d_t = map3dPointTo3d(layers[i + 1], layers[i + 1], p, n)
                    if p3d_t is None:
                        if not debug:
                            return None, None, None
                        else:
                            return p3d, i, None
                    p3d.append(p3d_t)
                # elif distances[i] == UVnormal:
                #    do nothing

        # for the synaptic layer, compute the uv-coordinates
        if i == (len(connections) - 1):
            p2d = map3dPointToUV(layers[i + 1], layers[i + 1], p3d_n)

    return p3d, p2d, compute_path_length(p3d)


def computeDistanceToSynapse(ilayer, slayer, p_3d, s_2d, dis):
    """ computes the distance between the last 3d-point and the synapse
    ilayer      : last intermediate layer
    slayer      : synaptic layer
    p_3d        : last 3d-point
    s_2d        : uv-coordinates of the synapse
    dis         : distance calculation technique
    """
    s_3d = mapUVPointTo3d(slayer, [s_2d])
    if not any(s_3d):
        logger.info("Need to exclude one connection")
        return -1, -1

    if dis == DIS_euclid:
        return (p_3d - s_3d[0]).length, s_3d

    elif dis == DIS_euclidUV:
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, s_3d[0], slayer)
        path.append(s_3d[0])
        return compute_path_length(path), path

    elif dis == DIS_jumpUV:
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, s_3d[0], slayer)
        path.append(s_3d[0])
        return compute_path_length(path), path

    elif dis == DIS_UVjump:
        i_3d = ilayer.closest_point_on_mesh(s_3d[0])[0]
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, i_3d, ilayer)
        path.append(i_3d)
        path.append(s_3d[0])
        return compute_path_length(path), path

    elif dis == DIS_normalUV:
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, s_3d[0], slayer)
        path.append(s_3d[0])
        return compute_path_length(path), path

    elif dis == DIS_UVnormal:
        p, n, f = slayers.closest_point_on_mesh(s_3d[0])
        t_3d = map3dPointTo3d(ilayers, ilayers, p, n)
        if t_3d is None:
            return -1, -1
        path = [p_3d]
        path = path + interpolateUVTrackIn3D(p_3d, t_3d, ilayers)
        path.append(t_3d)
        path.append(s_3d[0])
        return compute_path_length(path), path


# TODO(SK): missing docstring
def addConnection(*args):
    model.CONNECTIONS.append(args)

    # returns the future index of the connection
    return (len(model.CONNECTIONS) - 1)

# TODO(SK): ??? closing brackets are switched

#    model.CONNECTIONS.append(
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


# TODO(SK): missing docstring
def computeAllConnections():
    for c in model.CONNECTIONS:
        logger.info(c[0][0].name + ' - ' + c[0][-1].name)

        result = computeConnectivity(*c)
        model.CONNECTION_RESULTS.append(
            {
                'c': result[0],
                'd': result[1],
                's': result[2]
            }
        )


def updateMapping(index):
    """ Updates a mapping given by index """
    m = model.CONNECTIONS[index]
    result = computeConnectivity(*m, create=False)
    model.CONNECTION_RESULTS[index] = {
        'c': result[0],
        'd': result[1],
        's': result[2]
    }


# TODO(SK): missing docstring
def computeConnectivity(layers, neuronset1, neuronset2, slayer, connections,
                        distances, func_pre, args_pre, func_post, args_post,
                        no_synapses, create=True):
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
    create              : if create == True, then create new connection, otherwise it is just updated
    """
    # connection matrix
    conn = numpy.zeros((len(layers[0].particle_systems[neuronset1].particles), no_synapses)).astype(int)

    # distance matrix
    dist = numpy.zeros((len(layers[0].particle_systems[neuronset1].particles), no_synapses))

    # synapse mattrx (matrix, with the uv-coordinates of the synapses)
    syn = [[[] for j in range(no_synapses)] for i in range(len(layers[0].particle_systems[neuronset1].particles))]

    uv_grid = grid.UVGrid(layers[slayer], 0.02)

    # rescale arg-parameters
    args_pre = [i / layers[slayer]['uv_scaling'] for i in args_pre]
    args_post = [i / layers[slayer]['uv_scaling'] for i in args_post]

    logger.info("Prepare Grid")

    uv_grid.compute_pre_mask(func_pre, args_pre)
    uv_grid.compute_post_mask(func_post, args_post)

    logger.info("Compute Post-Mapping")

    # fill uv_grid with post-neuron-links
    for i in range(0, len(layers[-1].particle_systems[neuronset2].particles)):
        post_p3d, post_p2d, post_d = computeMapping(layers[:(slayer - 1):-1],
                                                    connections[:(slayer - 1):-1],
                                                    distances[:(slayer - 1):-1],
                                                    layers[-1].particle_systems[neuronset2].particles[i].location)
        if post_p3d is None:
            continue

        uv_grid.insert_postNeuron(i, post_p2d, post_p3d[-1], post_d)

    logger.info("Compute Pre-Mapping")
    num_particles = len(layers[0].particle_systems[neuronset1].particles)
    for i in range(0, num_particles):
        pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[i].location)

        logger.info(str(round((i / num_particles) * 10000) / 100) + '%')

        if pre_p3d is None:
            for j in range(0, len(conn[i])):
                conn[i, j] = -1
            continue

        post_neurons = uv_grid.select_random(pre_p2d, no_synapses)

        if (len(post_neurons) == 0):
            for j in range(0, len(conn[i])):
                conn[i, j] = -1
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
            conn[i, rest] = -1

    if create:
        model.CONNECTION_INDICES.append(
            [
                model.CONNECTION_COUNTER,
                model.NG_DICT[layers[0].name][neuronset1],
                model.NG_DICT[layers[-1].name][neuronset2]
            ]
        )
        model.CONNECTION_COUNTER += 1

    return conn, dist, syn, uv_grid


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
    conn = numpy.zeros((len(layers[0].particle_systems[neuronset1].particles),
                        len(layers[-1].particle_systems[neuronset2].particles)))

    # distance matrix
    dist = numpy.zeros((len(layers[0].particle_systems[neuronset1].particles),
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
    """ Print connection pairs """
    for i, c in enumerate(model.CONNECTION_INDICES):
        message = "%d: %s - %s" % (i, model.NG_LIST[c[1]][0],
                                   model.NG_LIST[c[2]][0])

        logger.info(message)


def computeDistance(layer1, layer2, neuronset1, neuronset2, common_layer,
                    connection_matrix):
    """Measures the distance between neurons on the same layer according to the
    connectivity matrix.

    layer1
    layer2            : layer of pre- and post-synaptic neurons
    neuronset1,
    neuronset2        : name of the neuronset (particlesystem)
    common_layer      : layer, on which the distances should be measured
    connection_matrix : connectivity matrix that determines, which distances
                        should be measured

    result            : matrix of the same structure, like connection_matrix,
                        but with distances
    """
    positions1 = []     # list of uv-positions for the first group
    positions2 = []     # list of uv-positions for the second group

    for p in layer1.particle_systems[neuronset1].particles:
        p2d = map3dPointToUV(common_layer, common_layer, p.location)
        positions1.append(p2d)

    for p in layer2.particle_systems[neuronset2].particles:
        p2d = map3dPointToUV(common_layer, common_layer, p.location)
        positions2.append(p2d)

    result = numpy.zeros(connection_matrix.shape)

    for i in range(len(connection_matrix)):
        for j in range(len(connection_matrix[i])):
            distance = (positions2[connection_matrix[i][j]] - positions1[i]).length
            result[i, j] = distance * common_layer['uv_scaling']

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

    for obj in objects:
        if obj.type == 'MESH':
            if any(obj.data.uv_layers):
                _, edges_scaled = computeUVScalingFactor(obj)
                uv_data.append(edges_scaled)
                layer_names.append(obj.name)

    return uv_data, layer_names


def initializeUVs():
    """ compute the UV scaling factor for all layers that have UV-maps """
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if any(obj.data.uv_layers):
                obj['uv_scaling'], _ = computeUVScalingFactor(obj)

            ''' area size of each polygon '''
            p_areas = []

            ''' collect area values for all polygons '''
            for p in obj.data.polygons:
                p_areas.append(p.area)

            # convert everything to numpy
            p_areas = numpy.array(p_areas)
            # compute the cumulative sum
            p_cumsum = p_areas.cumsum()
            # compute the sum of all areas
            p_sum = p_areas.sum()

            obj['area_cumsum'] = p_cumsum
            obj['area_sum'] = p_sum


def returnNeuronGroups():
    """Returns a list of neural groups (particle-systems) for the whole model.
    This is used for the NEST import to determine, which neural groups should
    be connected
    """

    r_list = []
    r_dict = {}
    counter = 0
    for obj in bpy.data.objects:
        for p in obj.particle_systems:
            r_list.append([obj.name, p.name, p.settings.count])
            if r_dict.get(obj.name) is None:
                r_dict[obj.name] = {}
            r_dict[obj.name][p.name] = counter
            counter += 1

    return r_list, r_dict


def resetOrigins():
    for c in model.CONNECTIONS:
        for l in c[0]:
            l.select = True
            bpy.context.scene.objects.active = l
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            l.select = False


def initialize3D():
    """prepares all necessary steps for the computation of connections"""

    logger.info("reset model")
    model.reset()

    logger.info("computing uv-scaling factor")
    initializeUVs()

    logger.info("collecting neuron groups")
    model.NG_LIST, model.NG_DICT = returnNeuronGroups()

    logger.info("done initalizing")
