# TODO(SK): module docstring missing

import logging

import bpy
import numpy

from . import pam
from . import model

logger = logging.getLogger(__package__)

vis_objects = 0


def setCursor(loc):
    """Just a more convenient way to set the location of the cursor"""

    bpy.data.screens['Default'].scene.cursor_location = loc


def getCursor():
    """Just returns the cursor location. A bit shorter to type ;)"""

    return bpy.data.screens['Default'].scene.cursor_location


def visualizePostNeurons(no_connection, pre_neuron):
    """visualizes the post-synaptic neurons that are connected with a given
    neuron from the presynaptic layer
    no_connection : connection index
    pre_neuron    : index of pre-synaptic neuron
    """

    global vis_objects

    layer = pam.pam_connections[no_connection][0][-1]  # get last layer of connection
    neuronset = pam.pam_connections[no_connection][2]  # neuronset 2
    connectivity = pam.pam_connection_results[no_connection]['c'][pre_neuron]

    for i in connectivity:
        if (i >= 0):
            bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=layer.particle_systems[neuronset].particles[i].location, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
            bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
            vis_objects = vis_objects + 1


def visualizePoint(point):
    """ visualizes a point in 3d by creating a small sphere """
    global vis_objects
    bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=point, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
    bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
    vis_objects = vis_objects + 1


def visualizePath(pointlist, smoothing=0):
    """ Create path for a given point list

    This code is taken and modified from the bTrace-Addon for Blender
    http://blenderartists.org/forum/showthread.php?214872  
    
    pointlist   : list of 3d-vectors that are converted to a path
    smoothing   : number of smoothing stepts that should be applied afterwards """

    global vis_objects

    # trace the origins
    tracer = bpy.data.curves.new('tracer', 'CURVE')
    tracer.dimensions = '3D'
    spline = tracer.splines.new('BEZIER')
    spline.bezier_points.add(len(pointlist) - 1)
    curve = bpy.data.objects.new('curve', tracer)
    bpy.context.scene.objects.link(curve)

    # render ready curve
    tracer.resolution_u = 8
    tracer.bevel_resolution = 8  # Set bevel resolution from Panel options
    tracer.fill_mode = 'FULL'
    tracer.bevel_depth = 0.005  # Set bevel depth from Panel options

    # move nodes to objects
    for i in range(0, len(pointlist)):
        p = spline.bezier_points[i]
        p.co = pointlist[i]
        p.handle_right_type = 'VECTOR'
        p.handle_left_type = 'VECTOR'

    bpy.context.scene.objects.active = curve
    bpy.ops.object.mode_set()
    curve.name = "visualization.%03d" % vis_objects

    vis_objects = vis_objects + 1
    
    # apply smoothing if requested
    if smoothing > 0:
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        for i in range(0, smoothing):
            bpy.ops.curve.smooth()
        bpy.ops.object.editmode_toggle()
        
    return curve


def visualizeForwardMapping(no_connection, pre_index):
    """ This is a debugging routine. The procedure tries to visualize the maximal
    amount of mappings to determine, where the mapping fails
    no_connection       : connection/mapping-index
    pre_index           : index of pre-synaptic neuron
    """
    layers = model.CONNECTIONS[no_connection][0]
    neuronset1 = model.CONNECTIONS[no_connection][1]
    neuronset2 = model.CONNECTIONS[no_connection][2]
    slayer = model.CONNECTIONS[no_connection][3]
    connections = model.CONNECTIONS[no_connection][4]
    distances = model.CONNECTIONS[no_connection][5]

    pre_p3d, pre_p2d, pre_d = pam.computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:(slayer - 1)] + [pam.DIS_euclidUV],
                                                 layers[0].particle_systems[neuronset1].particles[pre_index].location,
                                                 debug = True)
                                                 
    logger.debug(pre_p3d)
    visualizePath(pre_p3d)


def visualizeBackwardMapping(no_connection, post_index):
    """ This is a debugging routine. The procedure tries to visualize the maximal
    amount of mappings to determine, where the mapping fails
    no_connection       : connection/mapping-index
    post_index          : index of post-synaptic neuron
    """
    layers = model.CONNECTIONS[no_connection][0]
    neuronset1 = model.CONNECTIONS[no_connection][1]
    neuronset2 = model.CONNECTIONS[no_connection][2]
    slayer = model.CONNECTIONS[no_connection][3]
    connections = model.CONNECTIONS[no_connection][4]
    distances = model.CONNECTIONS[no_connection][5]

    for s in range(len(layers), slayer, -1):
        post_p3d, post_p2d, post_d = pam.computeMapping(layers[:(slayer - 1):-1],
                                                        connections[:(slayer - 1):-1],
                                                        distances[:(slayer - 1):-1],
                                                        layers[-1].particle_systems[neuronset2].particles[post_index].location)
        logger.debug(s)
        logger.debug(post_p3d)
        visualizePath(post_p3d)


def visualizeConnectionsForNeuron(no_connection, pre_index, smoothing=0):
    """ Visualizes all connections between a given pre-synaptic neuron and its connections
    to all post-synaptic neurons
    layers              : list of layers connecting a pre- with a post-synaptic layer
    neuronset1,
    neuronset2          : name of the neuronset (particle system) of the pre- and post-synaptic layer
    slayer              : index in layers for the synaptic layer
    connections         : list of values determining the type of layer-mapping
    distances           : list of values determining the calculation of the distances between layers
    pre_index           : index of pre-synaptic neuron
    post_indices        : index-list of post-synaptic neurons
    synapses            : optional list of coordinates for synapses
    """

    layers = model.CONNECTIONS[no_connection][0]
    neuronset1 = model.CONNECTIONS[no_connection][1]
    neuronset2 = model.CONNECTIONS[no_connection][2]
    slayer = model.CONNECTIONS[no_connection][3]
    connections = model.CONNECTIONS[no_connection][4]
    distances = model.CONNECTIONS[no_connection][5]

    post_indices = model.CONNECTION_RESULTS[no_connection]['c'][pre_index]
    synapses = model.CONNECTION_RESULTS[no_connection]['s'][pre_index]

    # path of the presynaptic neuron to the synaptic layer
    pre_p3d, pre_p2d, pre_d = pam.computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[pre_index].location)

    first_item = True

    for i in range(0, len(post_indices)):
        if post_indices[i] == -1:
            continue
        post_p3d, post_p2d, post_d = pam.computeMapping(layers[:(slayer - 1):-1],
                                                        connections[:(slayer - 1):-1],
                                                        distances[:(slayer - 1):-1],
                                                        layers[-1].particle_systems[neuronset2].particles[int(post_indices[i])].location)
        if synapses is None:
            visualizePath(pre_p3d + post_p3d[::-1])
        else:
            if (len(synapses[i]) > 0):
                distances_pre, pre_path = pam.computeDistanceToSynapse(
                    layers[slayer - 1], layers[slayer], pre_p3d[-1], synapses[i], distances[slayer - 1])
                if distances_pre >= 0:
                    distances_post, post_path = pam.computeDistanceToSynapse(
                        layers[slayer + 1], layers[slayer], post_p3d[-1], synapses[i], distances[slayer])
                    if (distances_post >= 0):
                        if first_item:
                            visualizePath(pre_p3d, smoothing)
                            visualizePath([pre_p3d[-1]] + pre_path + post_path[::-1] + post_p3d[::-1], smoothing)
                            first_item = False
                        else:
                            visualizePath([pre_p3d[-1]] + pre_path + post_path[::-1] + post_p3d[::-1], smoothing)

    if not first_item:
        return [pre_p3d[-1]] + pre_path + post_path[::-1] + post_p3d[::-1]
    else:
        return []


def visualizeOneConnection(no_connection, pre_index, post_index):
    """ Visualizes all connections between a given pre-synaptic and a given post-synaptic
    no_connection       : connection/mapping-id
    pre_index           : index of pre-synaptic neuron
    post_index          : index of post-synaptic neuron
    post_list_index     : index to be used in c[pre_index][post_list_index] to address post_index
    synapses            : optional list of coordinates for synapses
    """

    layers = model.CONNECTIONS[no_connection][0]
    neuronset1 = model.CONNECTIONS[no_connection][1]
    neuronset2 = model.CONNECTIONS[no_connection][2]
    slayer = model.CONNECTIONS[no_connection][3]
    connections = model.CONNECTIONS[no_connection][4]
    distances = model.CONNECTIONS[no_connection][5]

    synapses = model.CONNECTION_RESULTS[no_connection]['s'][pre_index]
    post_list_index = numpy.where(
        model.CONNECTION_RESULTS[no_connection]['c'][pre_index] == post_index
    )[0][0]

    # path of the presynaptic neuron to the synaptic layer
    pre_p3d, pre_p2d, pre_d = pam.computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[pre_index].location)

    post_p3d, post_p2d, post_d = pam.computeMapping(layers[:(slayer - 1):-1],
                                                    connections[:(slayer - 1):-1],
                                                    distances[:(slayer - 1):-1],
                                                    layers[-1].particle_systems[neuronset2].particles[post_index].location)
    if synapses is None:
        visualizePath(pre_p3d + post_p3d[::-1])
    else:
        distances_pre, pre_path = pam.computeDistanceToSynapse(
            layers[slayer - 1], layers[slayer], pre_p3d[-1], synapses[post_list_index], distances[slayer - 1])
        if distances_pre >= 0:
            distances_post, post_path = pam.computeDistanceToSynapse(
                layers[slayer + 1], layers[slayer], post_p3d[-1], synapses[post_list_index], distances[slayer])
            if distances_post >= 0:
                visualizePath(pre_p3d + pre_path + post_path[::-1] + post_p3d[::-1])


def visualizeNeuronSpread(connections, neuron):
    """ Visualizes for a collection of connections, the post-synaptic targets
    of a given neuron number of the first layer in the first connection and
    iteratively uses the post-synaptic targets as pre-synaptic neurons for
    the following connections
    connections     : list of connection-ids
    neuron          : neuron number for the pre-synaptic layer of the first
                      connection
    """
    visualizeConnectionsForNeuron(connections[0], neuron)
    if (len(connections) > 1):
        post_indices = model.CONNECTION_RESULTS[connections[0]]['c'][neuron]
        for post_index in post_indices[0:1]:
            if post_index >= 0:
                visualizeNeuronSpread(connections[1:], post_index)


def visualizeUnconnectedNeurons(no_connection):
    """ Visualizes unconnected neurons for a given connection_index """
    c = numpy.array(model.CONNECTION_RESULTS[no_connection]['c'])
    sums = numpy.array([sum(row) for row in c])
    indices = numpy.where(sums == -model.CONNECTIONS[no_connection][-1])[0]

    logger.debug(indices)

    layer = model.CONNECTIONS[no_connection][0][0]

    for index in indices:
        visualizePoint(layer.particle_systems[0].particles[index].location)


def visualizePartlyConnectedNeurons(no_connection):
    """ Visualizes neurons which are only partly connected """
    c = numpy.array(model.CONNECTION_RESULTS[no_connection]['c'])
    sums = numpy.array([sum(row) for row in c])
    indices = numpy.where(sums < model.CONNECTIONS[no_connection][-1])[0]

    logger.debug(indices)

    layer = model.CONNECTIONS[no_connection][0][0]

    for index in indices:
        visualizePoint(layer.particle_systems[0].particles[index].location)


def visualizeClean():
    """delete all visualization objects"""

    # delete all previous spheres
    global vis_objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="visualization*")
    bpy.ops.object.delete(use_global=False)
    vis_objects = 0
