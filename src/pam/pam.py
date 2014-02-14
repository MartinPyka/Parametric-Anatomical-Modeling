import bpy
import mathutils.geometry as mug
import mathutils
import math
import numpy as np

samples = 1000 # number of samples to compute connection probability
vis_objects = 0
debug_level = 0

def computeUVScalingFactor(object):
    ''' computes the scaling factor between uv- and 3d-coordinates for a 
    given object 
    the return value is the factor that has to be multiplied with the uv-coordinates
    in order to have metrical relations '''
    result = []
        
    for i in range(0, len(object.data.polygons)):
        uvs = [object.data.uv_layers.active.data[li] for li in object.data.polygons[i].loop_indices]    
        
        rdist = (object.data.vertices[object.data.polygons[i].vertices[0]].co - object.data.vertices[object.data.polygons[i].vertices[1]].co).length
        mdist = (uvs[0].uv - uvs[1].uv).length
        result.append(rdist/mdist)
    
    return np.mean(result)
    

def map3dPointToUV(object, object_uv, point):
    ''' Converts a given 3d-point into uv-coordinates,
    object for the 3d point and object_uv must have the same topology '''

    # get point, normal and face of closest point to particle
    p, n, f = object.closest_point_on_mesh(point)
    
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
    p_uv = mug.barycentric_transform(p,A,B,C,U,V,W)
    
    # if the point is not within the first triangle, we have to repeat the calculation 
    # for the second triangle
    if mug.intersect_point_tri_2d(p_uv.to_2d(), uvs[0].uv, uvs[1].uv, uvs[2].uv) == 0:
        A = object.data.vertices[object.data.polygons[f].vertices[0]].co
        B = object.data.vertices[object.data.polygons[f].vertices[2]].co
        C = object.data.vertices[object.data.polygons[f].vertices[3]].co
        
        U = uvs[0].uv.to_3d()
        V = uvs[2].uv.to_3d()
        W = uvs[3].uv.to_3d()
        
        p_uv = mug.barycentric_transform(p,A,B,C,U ,V,W)
    
    return p_uv.to_2d()


def map3dPointTo3d(o1, o2, point):
    ''' maps a 3d-point on a given object on another object. Both objects must have the 
    same topology '''
    
    # get point, normal and face of closest point to particle
    p, n, f = o1.closest_point_on_mesh(point)
    
    # if o1 and o2 are identical, there is nothing more to do
    if (o1 == o2):
        return p
    
    # get the vertices of the first triangle of the polygon from both objects
    A1 = o1.data.vertices[o1.data.polygons[f].vertices[0]].co
    B1 = o1.data.vertices[o1.data.polygons[f].vertices[1]].co
    C1 = o1.data.vertices[o1.data.polygons[f].vertices[2]].co 
    
    # project the point on a 2d-surface and check, whether we are in the right triangle
    t1 = mathutils.Vector();
    t2 = mathutils.Vector((1.0, 0.0, 0.0))
    t3 = mathutils.Vector((0.0, 1.0, 0.0))
    
    p_test = mug.barycentric_transform(p,A1,B1,C1,t1, t2, t3)
    
    # if the point is on the 2d-triangle, proceed with the real barycentric_transform
    if mug.intersect_point_tri_2d(p_test.to_2d(), t1.xy, t2.xy, t3.xy) == 1:
        A2 = o2.data.vertices[o2.data.polygons[f].vertices[0]].co
        B2 = o2.data.vertices[o2.data.polygons[f].vertices[1]].co
        C2 = o2.data.vertices[o2.data.polygons[f].vertices[2]].co    
        
        # convert 3d-coordinates of the point 
        p_new = mug.barycentric_transform(p,A1,B1,C1,A2,B2,C2)
        
    else:
        
        # use the other triangle
        A1 = o1.data.vertices[o1.data.polygons[f].vertices[0]].co
        B1 = o1.data.vertices[o1.data.polygons[f].vertices[2]].co
        C1 = o1.data.vertices[o1.data.polygons[f].vertices[3]].co 

        A2 = o2.data.vertices[o2.data.polygons[f].vertices[0]].co
        B2 = o2.data.vertices[o2.data.polygons[f].vertices[2]].co
        C2 = o2.data.vertices[o2.data.polygons[f].vertices[3]].co        
        
        # convert 3d-coordinates of the point 
        p_new = mug.barycentric_transform(p,A1,B1,C1,A2,B2,C2)
        
    ### TODO ###
    ### triangle check could be made more efficient ###
    ### check the correct triangle order !!! ###
    return p_new
    
def connfunc_gauss(u, v, *args):
    ''' Gauss-function for 2d 
        u, v    : coordinates, to determine the function value
        vu, vv  : variance for both dimensions
        su, sv  : shift in u and v direction
    '''
    vu = args[0][0]
    vv = args[0][1]
    su = args[0][2]
    sv = args[0][3]
    return math.exp(-( (u+su)**2/(2*vu**2) + (v+sv)**2/(2*vv**2) ))

def connfunc_unity(u, v, *args):
    return 1

def computeConnectivityProbability(uv1, uv2, func, args):
    return func(uv2[0]-uv1[0], uv2[1]-uv1[1], args)


def computeMapping(layers, connections, distances, point):
    ''' based on a list of layers, connections-properties and distance-properties,
    this function returns the 3d-point, the 2d-uv-point and the distance from a given
    point on the first layer to the corresponding point on the last layer 
    layers              : list of layers connecting the pre-synaptic layer with the synaptic layer
    connections         : list of values determining the type of layer-mapping
    distances           : list of values determining the calculation of the distances between layers
    point               : 3d vector for which the mapping should be calculated
    
    Return values
    -----------------
    p3d                 : 3d-vector of the neuron position on the last layer
    p2d                 : 2d-vector of the neuron position on the UV map of the last layer
    d                   : distance between neuron position on the first layer and last position before
                          the synapse! This is not the distance to the p3d point! This is either the 
                          distance to the 3d-position of the last but one layer or, in case
                          euclidean-uv-distance was used, the distance to the position of the last
                          layer determind by euclidean-distance. Functions, like computeConnectivity()
                          add the distance to the synapse to value d in order to retrieve
                          the complete distance from the pre- or post-synaptic neuron 
                          to the synapse
    '''
    
    p3d = point
    d = 0
    
    # go through all connection-elements
    for i in range(0, len(connections)):
        # if both layers are topologically identical
        if connections[i] == 1:
            p3d_n = map3dPointTo3d(layers[i], layers[i+1], p3d)
        else:
            p3d_n = map3dPointTo3d(layers[i+1], layers[i+1], p3d)

        # compute distance between both points, here according to the euclidean-uv-way
        if distances[i] == 1:
            # if we are not on the last layer
            if (i <= (len(connections)-1)):
                # determine closest point on second layer
                p3d_i = layers[i+1].closest_point_on_mesh(p3d)
                p3d_i = p3d_i[0]
                # compute uv-coordintes for euclidean distance and topological mapping
                p2d_i1 = map3dPointToUV(layers[i+1], layers[i+1], p3d)
                p2d_i2 = map3dPointToUV(layers[i], layers[i+1], p3d)
                # compute distances
                d = d + (p3d - p3d_i).length  # distance in space between both layers based on euclidean distance
                d = d + (p2d_i1 - p2d_i2).length * layers[i+1]['uv_scaling']  # distance on uv-level (incorporated with scaling parameter)
            else:   # if we are in the last layer
                # determine closest point on second layer
                p3d_i = layers[i+1].closest_point_on_mesh(p3d)
                p3d_i = p3d_i[0]
                d = d + (p3d - p3d_i).length  # distance in space between both layers based on euclidean distance
        else:
            if (i <= (len(connections)-1)):
                d = d + (p3d - p3d_n).length
            
        # for the synaptic layer, compute the uv-coordinates
        if (i == (len(connections)-1)):
            p2d = map3dPointToUV(layers[i+1], layers[i+1], p3d_n)
            
        p3d = p3d_n            
    
    return p3d, p2d, d


def computeConnectivity(layers, neuronset1, neuronset2, slayer, connections, distances, func, args):
    ''' computes the connectivity probability between all neurons of both neuronsets
    on a synaptic layer
    layers              : list of layers connecting a pre- with a post-synaptic layer
    neuronset1,
    neuronset2          : name of the neuronset (particle system) of the pre- and post-synaptic layer
    slayer              : index in layers for the synaptic layer
    connections         : list of values determining the type of layer-mapping
    distances           : list of values determining the calculation of the distances between layers
    func                : function of the connectivity kernel
    args                : argument list for the connectivity kernel
    '''
    
    # connection matrix
    conn = np.zeros((len(layers[ 0].particle_systems[neuronset1].particles), 
                     len(layers[-1].particle_systems[neuronset2].particles)))
                       
    # distance matrix
    dist = np.zeros((len(layers[ 0].particle_systems[neuronset1].particles), 
                     len(layers[-1].particle_systems[neuronset2].particles)))
                     
    for i in range(0, len(layers[ 0].particle_systems[neuronset1].particles)):
        # compute position, uv-coordinates and distance for the pre-synaptic neuron
        pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer+1)], 
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[i].location)
                                                 
        for j in range(0, len(layers[-1].particle_systems[neuronset2].particles)):
            # compute position, uv-coordinates and distance for the post-synaptic neuron
            post_p3d, post_p2d, post_d = computeMapping(layers[:(slayer-1):-1], 
                                                        connections[:(slayer-1):-1], 
                                                        distances[:(slayer-1):-1],
                                                        layers[-1].particle_systems[neuronset2].particles[j].location)
            
            # determine connectivity probabiltiy and distance values, incorporating the
            # uv-scaling value
            conn[i, j] = computeConnectivityProbability(pre_p2d * layers[slayer]['uv_scaling'], post_p2d * layers[slayer]['uv_scaling'], func, args)
            
            # depending on the value given in the distance-list for the synapse layer
            dist[i, j] = pre_d + post_d + (pre_p2d - post_p2d).length
     
    return conn, dist


#def computeConnectivity(l1, p1, l2, p2, al, l1t, l2t, func, args):
#    ''' computes the connectivity probability between two layers l1 and l2 using
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
    ''' prepares all necessary steps for the computation of connections '''
    
    # compute the UV scaling factor for all layers that have UV-maps 
    for o in bpy.data.objects:
        if o.type == 'MESH':
            if len(o.data.uv_layers) > 0:
                o['uv_scaling'] = computeUVScalingFactor(o)
    
def setCursor(loc):
    ''' Just a more convenient way to set the location of the cursor '''
    bpy.data.screens['Default'].scene.cursor_location = loc  
    
def getCursor():
    ''' Just returns the cursor location. A bit shorter to type ;) '''
    return bpy.data.screens['Default'].scene.cursor_location
    
    
def visualizePostNeurons(layer, neuronset, connectivity):
    ''' visualizes the post-synaptic neurons that are connected with a given
    neuron from the presynaptic layer 
    layer       : post-synaptic layer 
    neuronset   : name of the particlesystem
    connectivity: connectivity-vector '''
    
    global vis_objects
    
    for i in range(0, len(connectivity)):
        if connectivity[i] > 0.7:
             bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=layer.particle_systems[neuronset].particles[i].location, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
             bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
             bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
             vis_objects = vis_objects + 1
             
def visualizePoint(point):
    ''' visualizes a point in 3d by creating a small sphere '''
    global vis_objects    
    bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=point, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
    bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
    vis_objects = vis_objects + 1
    
def visualizeClean():
    ''' delete all visualization objects '''    
    # delete all previous spheres
    global vis_objects    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="visualization*")
    bpy.ops.object.delete(use_global=False)   
    vis_objects = 0 

dg = bpy.data.objects['DG_sg']
ca3 = bpy.data.objects['CA3_sp']
ca1 = bpy.data.objects['CA1_sp']
al_dg = bpy.data.objects['DG_sg_axons_all']
al_ca3 = bpy.data.objects['CA3_sp_axons_all']


##############################################################################################
## Main Code:
## Here the connectivity between two layers using an intermediate layer 
##############################################################################################
# preparatory steps are done in initialize3D (e.g. calculating the uv-scaling-factor for all 
# meshs with uv-data. 
print('Initialize data')
initialize3D()

# connect ca3 with ca3 using an intermediate layer al_ca3. first relationship is topological, 
# second one is euclidian
# use a gauss-function with given variance and shifting parameters to determine the connectivity

print('Compute Connectivity for ca3 to ca3')
#c_ca3_ca3 = computeConnectivity(ca3, 'CA3_Pyramidal', 
#                                ca3, 'CA3_Pyramidal', 
#                                al_ca3, 
#                                1, 0, 
#                                connfunc_gauss, [3.0, 0.3, 2.3, 0.00])

params = [10., 3., 5., 0.00]

c_ca3_ca3, d_ca3_ca3 = computeConnectivity([ca3, al_ca3, ca3],                     # layers involved in the connection
                                            'CA3_Pyramidal', 'CA3_Pyramidal',       # neuronsets involved
                                            1,                                      # synaptic layer
                                            [1, 0],                                 # connection mapping
                                            [1, 0],                                 # distance calculation
                                            connfunc_gauss, params)   # kernel function plus parameters

print('Compute Connectivity for ca3 to ca1')

c_ca3_ca1, d_ca3_ca1 = computeConnectivity([ca3, al_ca3, ca1],                      # layers involved in the connection
                                            'CA3_Pyramidal', 'CA1_Pyramidal',       # neuronsets involved
                                            1,                                      # synaptic layer
                                            [1, 0],                                 # connection mapping
                                            [1, 0],                                 # distance calculation
                                            connfunc_gauss, params)   # kernel function plus parameters



#c_ca3_ca1 = computeConnectivity(ca3, 'CA3_Pyramidal', ca1, 'CA1_Pyramidal', al_ca3, 1, 0, connfunc_gauss, [3.0, 0.3, 2.3, 0.00])

## the rest is just for visualization
visualizeClean()

particle = 26

setCursor(ca3.particle_systems['CA3_Pyramidal'].particles[particle].location)

#print(c_ca3_ca3[particle])

visualizePostNeurons(ca3, 'CA3_Pyramidal', c_ca3_ca3[particle])
visualizePostNeurons(ca1, 'CA1_Pyramidal', c_ca3_ca1[particle])

#t1 = bpy.data.objects['t1']
#t2 = bpy.data.objects['t2']
#t3 = bpy.data.objects['t3']
#t4 = bpy.data.objects['t4']
#t5 = bpy.data.objects['t5']
#
#point = getCursor()
#
#p3, p2, d = computeMapping([t1, t2, t3, t4, t5], [1, 1, 1, 1], [0, 0, 0, 1], point)
#print(p3)
#print(p2)
#print(d)
#
#visualizePoint(p3)