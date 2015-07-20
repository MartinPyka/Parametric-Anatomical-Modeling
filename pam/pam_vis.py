# TODO(SK): module Missing docstring

import logging

import bpy
import numpy

from . import pam
from . import model
from . import colormaps

logger = logging.getLogger(__package__)

vis_objects = 0


def setCursor(loc):
    """Just a more convenient way to set the location of the cursor"""

    bpy.data.screens['Default'].scene.cursor_location = loc


def getCursor():
    """Just return the cursor location. A bit shorter to type ;)"""

    return bpy.data.screens['Default'].scene.cursor_location


def visualizePostNeurons(no_connection, pre_neuron):
    """Visualize the post-synaptic neurons that are connected with a given
    neuron from the presynaptic layer

    :param int no_connection: connection index
    :param int pre_neuron: index of pre-synaptic neuron

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


def generateLayerNeurons(layer, particle_system, obj, object_color=[],
                         indices=-1):
    """Generate for each particle (neuron) a cone with appropriate naming"""
    # generate first mesh
    i = 0
    p = layer.particle_systems[particle_system].particles[0]

    if indices == -1:
        particles = layer.particle_systems[particle_system].particles
    else:
        particles = layer.particle_systems[particle_system].particles[indices[0]:indices[1]]

    # generates linked duplicates of this mesh
    for i, p in enumerate(particles):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = obj
        bpy.context.object.select = True

        bpy.ops.object.duplicate(linked=True, mode='INIT')
        dupli = bpy.context.active_object
        dupli.name = 'n' + '_' + layer.name + '_' + '%05d' % (i + 1)
        dupli.location = p.location
        if object_color:
            dupli.color = object_color[i]


def getColors(colormap, v, interval=[], alpha=True):
    """Based on a colormaps, values in the vector are converted to colors
    from the colormap

    :param list colormap: colormap to be used
    :param list v: list of values
    :param list interval: min and maximal range to be used, if empty these
                          values are computed based on v
    """
    if not interval:
        interval.append(min(v))
        interval.append(max(v))

    l = len(colormap) - 1
    span = float(interval[1] - interval[0])
    colors = []

    for i in v:
        ind = int(numpy.floor(((i - interval[0]) / span) * l))
        ind = max(min(l, ind), 0)
        if alpha:
            colors.append(colormap[ind])
        else:
            colors.append(colormap[ind][:3])
    return colors


def visualizeNeuronProjLength(no_connection, obj):
    """Visualizes the connection-length of the pre-synaptic neurons for a given
    mapping-index

    :param int no_connection: connection index (mapping index)

    """
    global vis_objects
    layers = model.CONNECTIONS[no_connection][0][0]  # get first layer
    neuronset1 = model.CONNECTIONS[no_connection][1]

    ds = numpy.mean(model.CONNECTION_RESULTS[no_connection]['d'], 1)
    colors = getColors(colormaps.standard, ds)

    generateLayerNeurons(layers, neuronset1, obj, colors)


def visualizePoint(point):
    """Visualize a point in 3d by creating a small sphere"""
    global vis_objects
    bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=point, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
    bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
    vis_objects = vis_objects + 1


def visualizePath(pointlist, smoothing=0):
    """Create path for a given point list

    :param list pointlist: 3d-vectors that are converted to a path
    :param list smoothing: smoothing stepts that should be applied afterwards

    This code is taken and modified from the bTrace-Addon for Blender
    http://blenderartists.org/forum/showthread.php?214872

    """

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
    """This is a debugging routine. The procedure tries to visualize the maximal
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

    for s in range(2, (slayer + 1)):
        pre_p3d, pre_p2d, pre_d = pam.computeMapping(
            layers[0:s],
            connections[0:(s - 1)],
            distances[0:(s - 2)] + [pam.DIS_euclidUV],
            layers[0].particle_systems[neuronset1].particles[pre_index].location,
            debug=True
        )
        logger.debug(s)
        logger.debug(pre_p3d)
        logger.debug(pre_p2d)
        logger.debug(pre_d)
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
        return visualizePath(pre_p3d + post_p3d[::-1])
    else:
        distances_pre, pre_path = pam.computeDistanceToSynapse(
            layers[slayer - 1], layers[slayer], pre_p3d[-1], synapses[post_list_index], distances[slayer - 1])
        if distances_pre >= 0:
            distances_post, post_path = pam.computeDistanceToSynapse(
                layers[slayer + 1], layers[slayer], post_p3d[-1], synapses[post_list_index], distances[slayer])
            if distances_post >= 0:
                return visualizePath(pre_p3d + pre_path + post_path[::-1] + post_p3d[::-1])


def visualizeNeuronSpread(connections, neuron):
    """Visualize for a collection of connections, the post-synaptic targets
    of a given neuron number of the first layer in the first connection and
    iteratively uses the post-synaptic targets as pre-synaptic neurons for
    the following connections

    :param list connections: list of connection-ids
    :param int neuron: neuron number for the pre-synaptic layer of the first
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


def polygons_coordinate(obj):
    r = []
    for p in obj.data.polygons:
        co = []
        for v in p.vertices:
            co.append(obj.data.vertices[v].co)
        r.append(co)
    return r


def color_polygons(obj, colors):
    if len(obj.data.polygons) != len(colors):
        raise Exception("number of colors given does not match polgyons")

    if not obj.data.vertex_colors:
        obj.data.vertex_colors.new()

    vc = obj.data.vertex_colors.active

    for c, p in zip(colors, obj.data.polygons):
        for v in p.loop_indices:
            vc.data[v].color = c


def vertices_coordinate(obj):
    return [v.co for v in obj.data.vertices]


def color_vertices(obj, colors):
    if len(obj.data.vertices) != len(colors):
        raise Exception("number of colors given does not match vertices")

    if not obj.data.vertex_colors:
        obj.data.vertex_colors.new()

    vc = obj.data.vertex_colors.active

    vc_index = [v for p in obj.data.polygons for v in p.vertices]

    for i, n in enumerate(vc_index):
        vc.data[i].color = colors[n]


# TODO(SK): Parameter types
def colorize_vertices(obj, v, interval=[]):
    """Colorize vertices of an object based on values in v and a
    given interval

    :param bpy.types.Object obj: objects, whose vertices should be used
    :param (???) v: vector length must correspond to number of vertices
    :param interval: min and maximal range. if empty, it will be computed
                     based on v

    """
    colors = getColors(colormaps.standard, v, interval, alpha=False)
    color_vertices(obj, colors)


def visualizeMappingDistance(no_mapping):
    """ visualizes the mapping distance for a pre-synaptic layer and a given
    mapping. The mapping distance is visualized by colorizing the vertices
    of the layer """
    layers = model.CONNECTIONS[no_mapping][0]
    neuronset1 = model.CONNECTIONS[no_mapping][1]

    distances = []

    for ds in model.CONNECTION_RESULTS[no_mapping]['d']:
        distances.append(numpy.mean(ds))

    colorize_vertices(layers[0], distances)


def computeAxonLengths(no_connection, pre_index, visualize=False):
    """ Computes the axon length to each synapse for each post-synaptic neuron the pre-
    synaptic neuron is connected with
    no_connection       : connection/mapping-id
    pre_index           : index of pre-synaptic neuron
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
    
    result = []

    for i in range(0, len(post_indices)):
        if post_indices[i] == -1:
            continue

        if synapses is None:
            result.append(pam.compute_path_length(pre_p3d))
        else:
            if (len(synapses[i]) > 0):
                distances_pre, pre_path = pam.computeDistanceToSynapse(
                    layers[slayer - 1], layers[slayer], pre_p3d[-1], synapses[i], distances[slayer - 1])
                result.append(pam.compute_path_length(pre_p3d + pre_path))
                if visualize:
                    visualizePath(pre_p3d + pre_path)
    return result


def hideAllLayers():
    """ Hide all layers involved in all mappings. If a layer occurs multiple times
    it is also called here multiple times """
    for m in model.CONNECTIONS:
        for layer in m[0]:
            layer.hide = True
            
def showMappingLayers(index):
    """ shows for a given mapping all layers involved in but hides everything else """
    hideAllLayers()
    for layer in model.CONNECTIONS[index][0]:
        layer.hide = False
        
def showPrePostLayers():
    """ shows for all mappings all the pre- and post-layers and hides everything else """
    hideAllLayers()
    for m in model.CONNECTIONS:
        m[0][0].hide = False
        m[0][-1].hide = False
