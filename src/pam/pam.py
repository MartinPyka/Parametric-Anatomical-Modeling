import bpy
import mathutils.geometry as mug
import mathutils
import math
import numpy as np
import random

# import module for visualization
import pam_vis as pv
# model with some hard-coded constants
import config as cfg

from . import helper

# number of samples to compute connection probability
samples = 1000
debug_level = 0

cfg.ray_fac = 1.0



def computePoint(v1, v2, v3, v4, x1, x2):
    # computes an average point on the polygon depending on x1 and x2
    mv12_co = v1.co * x1 + v2.co * (1-x1)
    mv34_co = v3.co * (1-x1) + v4.co * x1
    mv_co = mv12_co * x2 + mv34_co * (1-x2)
    
    return mv_co

def selectRandomPoint(object):
        # select a random polygon
        p_select = random.random() * object['area_sum']
        polygon = object.data.polygons[np.nonzero(np.array(object['area_cumsum']) > p_select)[0][0]]
        
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
        result.append(rdist/mdist)

    return np.mean(result)
    


# TODO(SK): Quads into triangles (indices)
def map3dPointToUV(object, object_uv, point, normal=None):
    """Converts a given 3d-point into uv-coordinates,
    object for the 3d point and object_uv must have the same topology
    if normal is not None, the normal is used to detect the point on object, otherwise
    the closest_point_on_mesh operation is used
    """ 

    # if normal is None, we don't worry about orthogonal projections
    if normal == None:
        # get point, normal and face of closest point to a given point 
        p, n, f = object.closest_point_on_mesh(point)
    else:
        p, n, f = object.ray_cast(point + normal * cfg.ray_fac, point - normal * cfg.ray_fac)
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
    p_uv = mug.barycentric_transform(p, A, B, C, U, V, W)

    # if the point is not within the first triangle, we have to repeat the calculation
    # for the second triangle
    if mug.intersect_point_tri_2d(p_uv.to_2d(), uvs[0].uv, uvs[1].uv, uvs[2].uv) == 0:
        A = object.data.vertices[object.data.polygons[f].vertices[0]].co
        B = object.data.vertices[object.data.polygons[f].vertices[2]].co
        C = object.data.vertices[object.data.polygons[f].vertices[3]].co

        U = uvs[0].uv.to_3d()
        V = uvs[2].uv.to_3d()
        W = uvs[3].uv.to_3d()

        p_uv = mug.barycentric_transform(p, A, B, C, U, V, W)

    return p_uv.to_2d()


def map3dPointTo3d(o1, o2, point, normal=None):
    """maps a 3d-point on a given object on another object. Both objects must have the
    same topology
    """

    # if normal is None, we don't worry about orthogonal projections
    if normal == None:
        # get point, normal and face of closest point to a given point 
        p, n, f = o1.closest_point_on_mesh(point)
    else:
        p, n, f = o1.ray_cast(point + normal * cfg.ray_fac, point - normal * cfg.ray_fac)
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

    p_test = mug.barycentric_transform(p, A1, B1, C1, t1, t2, t3)

    # if the point is on the 2d-triangle, proceed with the real barycentric_transform
    if mug.intersect_point_tri_2d(p_test.to_2d(), t1.xy, t2.xy, t3.xy) == 1:
        A2 = o2.data.vertices[o2.data.polygons[f].vertices[0]].co
        B2 = o2.data.vertices[o2.data.polygons[f].vertices[1]].co
        C2 = o2.data.vertices[o2.data.polygons[f].vertices[2]].co

        # convert 3d-coordinates of the point
        p_new = mug.barycentric_transform(p, A1, B1, C1, A2, B2, C2)

    else:

        # use the other triangle
        A1 = o1.data.vertices[o1.data.polygons[f].vertices[0]].co
        B1 = o1.data.vertices[o1.data.polygons[f].vertices[2]].co
        C1 = o1.data.vertices[o1.data.polygons[f].vertices[3]].co
        
        A2 = o2.data.vertices[o2.data.polygons[f].vertices[0]].co
        B2 = o2.data.vertices[o2.data.polygons[f].vertices[2]].co
        C2 = o2.data.vertices[o2.data.polygons[f].vertices[3]].co

        # convert 3d-coordinates of the point
        p_new = mug.barycentric_transform(p, A1, B1, C1, A2, B2, C2)

    # TODO(MP): triangle check could be made more efficient
    # TODO(MP): check the correct triangle order !!!
    return p_new


def connfunc_gauss_post(u, v, *args):
    """Gauss-function for 2d
    u, v    : coordinates, to determine the function value
    vu, vv  : variance for both dimensions
    su, sv  : shift in u and v direction
    """

    vu = args[0][0]
    vv = args[0][1]
    su = args[0][2]
    sv = args[0][3]

    return math.exp(-((u + su) ** 2 / (2 * vu ** 2) +
                    (v + sv) ** 2 / (2 * vv ** 2)))

    # TODO(MP): Kernel definition must be equal across code fragments
    # TODO(MP): Kernel functions can moved to separate module
    
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
    return func(uv2[0]-uv1[0], uv2[1]-uv1[1], args)


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
    p3d                 : list of 3d-vector of the neuron position on all layers
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
        
        
        # if euclidean mapping should be computed
        if connections[i] == cfg.MAP_euclid:
            # compute the point on the next intermediate layer
            if (i < (len(connections)-1)):
                p3d_n = map3dPointTo3d(layers[i+1], layers[i+1], p3d[-1])
                d = d + (p3d[-1] - p3d_n).length 
            # or the last point before the synaptic layer
            else:
                # for euclidean distance
                if distances[i] == cfg.DIS_euclid:
                    # p3d_n = p3d[-1]
                    p3d_n = map3dPointTo3d(layers[i+1], layers[i+1], p3d[-1])
                # for normal-uv or euclidean-uv mapping
                elif (distances[i] == cfg.DIS_normalUV) | (distances[i] == cfg.DIS_euclidUV):
                    p3d_n = map3dPointTo3d(layers[i+1], layers[i+1], p3d[-1])
                    d = d + (p3d[-1] - p3d_n).length
                    
                    
        # if normal mapping should be computed
        elif connections[i] == cfg.MAP_normal:
            # compute normal on layer for the last point
            p, n, f = layers[i].closest_point_on_mesh(p3d[-1])
            # determine new point
            p3d_n = map3dPointTo3d(layers[i+1], layers[i+1], p3d[-1], n)
            # if there is no intersection, abort
            if (p3d_n == None):
                return None, None, None
            if (i < (len(connections)-1)):
                d = d + (p3d[-1] - p3d_n).length 
            else:
                #if distances[i] == cfg.DIS_euclid:
                #    p3d_n = p3d[-1]
                if (distances[i] == cfg.DIS_normalUV) | (distances[i] == cfg.DIS_euclidUV):
                    d = d + (p3d[-1] - p3d_n).length 
                    
        # if random mapping should be used                    
        elif connections[i] == cfg.MAP_random:
            # if this is not the synapse layer
            if (i < (len(connections)-1)):
                p, n, f = selectRandomPoint(layers[i+1])
                p3d_n = p

                # for euclidean and euclideanUV-distance
                if (distances[i] == cfg.DIS_euclid) | (distances[i] == cfg.DIS_euclidUV):
                    d = d + (p3d[-1] - p3d_n).length 
                # for normal-uv-distance,     
                elif distances[i] == cfg.DIS_normalUV:
                    # determine closest point on second layer
                    p3d_i = layers[i+1].closest_point_on_mesh(p3d[-1])
                    p3d_i = p3d_i[0]
                    # compute uv-coordintes for euclidean distance and topological mapping
                    p2d_i1 = map3dPointToUV(layers[i+1], layers[i+1], p3d[-1])
                    p2d_i2 = map3dPointToUV(layers[i+1], layers[i+1], p3d_n)
                    # compute distances
                    d = d + (p3d[-1] - p3d_i).length  # distance in space between both layers based on euclidean distance
                    d = d + (p2d_i1 - p2d_i2).length * layers[i+1]['uv_scaling']  # distance on uv-level (incorporated with scaling parameter)
                    p3d.append(p3d_i)
            # if this is the last layer, compute the last p3d-point depending on the 
            # distance value
            else:
                # for euclidean distance
                #if distances[i] == cfg.DIS_euclid:
                    # remain at the last position
                #    p3d_n = p3d[-1]
                # for normal-uv-distance,     
                if distances[i] == cfg.DIS_normalUV:
                    # get the point on the next layer according to the normal
                    p3d_i = map3dPointTo3d(layers[i+1], layers[i+1], p3d[-1])
                    d = d + (p3d[-1] - p3d_i).length
                    p3d.append(p3d_i)
                # for euclidean-uv distance
                elif distances[i] == cfg.DIS_euclidUV:
                    # compute the topologically corresponding point
                    d = d + (p3d[-1] - p3d_n).length

                
                    
                    
        # if both layers are topologically identical
        elif connections[i] == cfg.MAP_top:
            
            # if this is not the last layer, compute the topological mapping
            if (i < (len(connections)-1)):         
                p3d_n = map3dPointTo3d(layers[i], layers[i+1], p3d[-1])
                
                # for euclidean and euclideanUV-distance
                if (distances[i] == cfg.DIS_euclid) | (distances[i] == cfg.DIS_euclidUV):
                    d = d + (p3d[-1] - p3d_n).length 
                # for normal-uv-distance,     
                elif distances[i] == cfg.DIS_normalUV:
                    # determine closest point on second layer
                    p3d_i = layers[i+1].closest_point_on_mesh(p3d[-1])
                    p3d_i = p3d_i[0]
                    # compute uv-coordintes for euclidean distance and topological mapping
                    p2d_i1 = map3dPointToUV(layers[i+1], layers[i+1], p3d[-1])
                    p2d_i2 = map3dPointToUV(layers[i+1], layers[i+1], p3d_n)
                    # compute distances
                    d = d + (p3d[-1] - p3d_i).length  # distance in space between both layers based on euclidean distance
                    d = d + (p2d_i1 - p2d_i2).length * layers[i+1]['uv_scaling']  # distance on uv-level (incorporated with scaling parameter)
                    p3d.append(p3d_i)
                
                
            # if this is the last layer, compute the last p3d-point depending on the 
            # distance value
            else:
                # for euclidean distance
                if distances[i] == cfg.DIS_euclid:
                    # remain at the last position
                    #p3d_n = p3d[-1]
                    p3d_n = map3dPointTo3d(layers[i], layers[i+1], p3d[-1])
                # for normal-uv-distance,     
                elif distances[i] == cfg.DIS_normalUV:
                    # get the point on the next layer according to the normal
                    p3d_i = map3dPointTo3d(layers[i+1], layers[i+1], p3d[-1])
                    p3d.append(p3d_i)
                    d = d + (p3d[-1] - p3d_i).length
                    p3d_n = map3dPointTo3d(layers[i], layers[i+1], p3d[-1])
                # for euclidean-uv distance
                elif distances[i] == cfg.DIS_euclidUV:
                    # compute the topologically corresponding point
                    p3d_n = map3dPointTo3d(layers[i], layers[i+1], p3d[-1])
                    d = d + (p3d[-1] - p3d_n).length

        # for the synaptic layer, compute the uv-coordinates
        if (i == (len(connections)-1)):
            p2d = map3dPointToUV(layers[i+1], layers[i+1], p3d_n)

        p3d.append(p3d_n)

    return p3d, p2d, d


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
        pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer+1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[i].location)
        if pre_p3d == None:
            continue

        for j in range(0, len(layers[-1].particle_systems[neuronset2].particles)):
            # compute position, uv-coordinates and distance for the post-synaptic neuron
            post_p3d, post_p2d, post_d = computeMapping(layers[:(slayer-1):-1],
                                                        connections[:(slayer-1):-1],
                                                        distances[:(slayer-1):-1],
                                                        layers[-1].particle_systems[neuronset2].particles[j].location)
            
            if post_p3d == None:
                continue                                                        

            # determine connectivity probabiltiy and distance values
            conn[i, j] = computeConnectivityProbability(pre_p2d * layers[slayer]['uv_scaling'], post_p2d * layers[slayer]['uv_scaling'], func, args)
            # for euclidean distance
            if distances[slayer-1] == 0:
                dist[i, j] = pre_d + post_d + (post_p3d[-1] - pre_p3d[-2]).length
            # for normal-uv-distance
            elif  distances[slayer-1] == 1:
                dist[i, j] = pre_d + post_d + (post_p2d - pre_p2d).length * layers[slayer]['uv_scaling']
            # for euclidean-uv-distances
            elif distances[slayer-1] == 2:
                dist[i, j] = pre_d + post_d + (post_p2d - pre_p2d).length * layers[slayer]['uv_scaling']
                
    return conn, dist


def computeConnectivity(layers, neuronset1, neuronset2, slayer, 
                        connections, distances, 
                        func_pre, args_pre, func_post, args_post, 
                        no_synapses ):
    ''' Computes for each pre-synaptic neuron no_synapses connections to post-synaptic neurons
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
    '''
    # connection matrix
    conn = np.zeros((len(layers[0].particle_systems[neuronset1].particles), no_synapses))

    # distance matrix
    dist = np.zeros((len(layers[0].particle_systems[neuronset1].particles), no_synapses))
    
    grid = helper.UVGrid(layers[slayer])
    grid.kernel = func_post
    
    # fill grid with post-neuron-links
    for i in range(0, len(layers[-1].particle_systems[neuronset2].particles)):
        post_p3d, post_p2d, post_d = computeMapping(layers[:(slayer-1):-1],
                                                    connections[:(slayer-1):-1],
                                                    distances[:(slayer-1):-1],
                                                    layers[-1].particle_systems[neuronset2].particles[j].location)
        grid.compute_kernel(i, post_p2d[0], post_p2d[1], args_post )
        
    for i in range(0, len(layers[0].particle_systems[neuronset1].particles)):
        pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer+1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[i].location)
        cell_uv = pre_p2d + func_pre(pre_p2d[0], pre_p2d[1], args_pre)
        cell = grid.cell(cell_uv[0], cell_uv[1])
        weights = sum([w[1] for w in cell])


#computeConnectivity([ca3, al_ca3, ca3],                     # layers involved in the connection
#                    'CA3_Pyramidal', 'CA3_Pyramidal',       # neuronsets involved
#                    1,                                      # synaptic layer
#                    [1, 0],                                 # connection mapping
#                    [1, 0],                                 # distance calculation
#                    connfunc_gauss, [3.0, 0.3, 2.3, 0.00],  # kernel function plus parameters for pre-neurons
#                    connfunc_gauss, [0.1, 0.1, 0.0, 0.00],  # kernel function plus parameters for pre-neurons
#                    300)                                    # number of connections of each pre-synaptic 
                                                            # neuron to post-synaptic neurons

#def computeConnectivity(l1, p1, l2, p2, al, l1t, l2t, func, args):
#    """computes the connectivity probability between two layers l1 and l2 using
#    an axon layer al
#    l1, l2      : layers with neuronsets (with particlesystems)
#    p1, p2      : name of the neuronsets (particlesystems)
#    al          : axon layer
#    l1t, l2t    : 1, if topologically identical with al, 0, if not '''
#
#    result = np.zeros((len(l1.particle_systems[p1].particles), len(l2.particle_systems[p2].particles)))
#    
#    # go through all neurons of l1 
#    for i in range(0, len(l1.particle_systems[p1].particles)):
#        # get uv-coordinates of the neuron on al-layer
#        if l1t == 1:
#            a_uv_l1 = map3dPointToUV(l1, al, l1.particle_systems[p1].particles[i].location)
#        else: 
#            a_uv_l1 = map3dPointToUV(al, al, l1.particle_systems[p1].particles[i].location)            
#
#        # go through all neurons of l2
#        for j in range(0, len(l2.particle_systems[p2].particles)):
#            # get uv-coordinate of the neuron on al-layer        
#            if l2t == 1:
#                a_uv_l2 = map3dPointToUV(l2, al, l2.particle_systems[p2].particles[j].location)
#            else:
#                a_uv_l2 = map3dPointToUV(al, al, l2.particle_systems[p2].particles[j].location)
#            
#            result[i, j] = computeConnectivityProbability(a_uv_l1, a_uv_l2, func, args)   
#            
#    return result


def initialize3D():
    """prepares all necessary steps for the computation of connections"""

    # compute the UV scaling factor for all layers that have UV-maps
    for o in bpy.data.objects:
        if o.type == 'MESH':
            if len(o.data.uv_layers) > 0:
                o['uv_scaling'] = computeUVScalingFactor(o)
                
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


def test():
    """ Just a routine to perform some tests """
    initialize3D()
    pv.visualizeClean()
    
    t1 = bpy.data.objects['t1']
    t2 = bpy.data.objects['t2']
    t201 = bpy.data.objects['t2.001']
    t3 = bpy.data.objects['t3']
    t4 = bpy.data.objects['t4']
    t5 = bpy.data.objects['t5']
	
    point, n, p = t1.closest_point_on_mesh(pv.getCursor())
	
    p3, p2, d = computeMapping([t1, t2, t201, t3, t4, t5], 
                               [cfg.MAP_normal, cfg.MAP_top, cfg.MAP_top, cfg.MAP_top, cfg.MAP_top], 
                               [cfg.DIS_euclid, cfg.DIS_euclid, cfg.DIS_euclid, cfg.DIS_euclid, cfg.DIS_euclid], 
                               point)
    print(p3)
    print(p2)
    print(d)
	
    if (p3 != None):
        pv.visualizePath(p3)
    
    
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
                                                  [cfg.MAP_top, cfg.MAP_euclid],                                 # connection mapping
                                                  [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
                                                  connfunc_gauss, params)   # kernel function plus parameters                                               
        
    print('Compute Connectivity for ca3 to ca1')
    c_ca3_ca1, d_ca3_ca1 = computeConnectivityAll([ca3, al_ca3, ca1],                      # layers involved in the connection
                                                 'CA3_Pyramidal', 'CA1_Pyramidal',       # neuronsets involved
                                                 1,                                      # synaptic layer
                                                 [cfg.MAP_top, cfg.MAP_euclid],                                 # connection mapping
                                                 [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
                                                 connfunc_gauss, params)   # kernel function plus parameters
    
    
    
	#c_ca3_ca1 = computeConnectivity(ca3, 'CA3_Pyramidal', ca1, 'CA1_Pyramidal', al_ca3, 1, 0, connfunc_gauss, [3.0, 0.3, 2.3, 0.00])
    
	## the rest is just for visualization
    pv.visualizeClean()
    
    particle = 40
    
    pv.setCursor(ca3.particle_systems['CA3_Pyramidal'].particles[particle].location)
    
    pv.visualizePostNeurons(ca3, 'CA3_Pyramidal', c_ca3_ca3[particle])
    pv.visualizePostNeurons(ca1, 'CA1_Pyramidal', c_ca3_ca1[particle])
    
#    p3, p2, d = computeMapping([ca3, al_ca3], 
#                               [cfg.MAP_top], 
#                               [cfg.DIS_normalUV], 
#                               ca3.particle_systems['CA3_Pyramidal'].particles[particle].location)    
#    print(p3)
#    if (p3 != None):
#        pv.visualizePath(p3)                               
    
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
                                                
    pv.visualizeClean()
    
    particle = 44
    
    pv.setCursor(ca1.particle_systems['CA1_Pyramidal'].particles[particle].location)
    
    pv.visualizePostNeurons(ca1, 'CA1_Pyramidal', c_ca1_sub[particle])
                                               


if __name__ == "__main__":
    ##############################################################################################
    ## Main Code:
    ## Here the connectivity between two layers using an intermediate layer
    ##############################################################################################

    #test() 
    hippotest()
    #subiculumtest()
       

