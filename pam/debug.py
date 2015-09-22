from pam import model
from pam import pam

import bpy
import numpy
import logging

logger = logging.getLogger(__package__)

def getUniqueUVMapErrors():
    errors = {}
    for err in model.CONNECTION_ERRORS:
        if str(err) not in errors:
            errors[str(err)] = err
    return list(errors.values())

def showErrorOnUVMap(err):
    bpy.context.scene.objects.active = err.layer
    err.layer.select = True
    bpy.ops.object.mode_set()
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action = 'SELECT')

    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':   #find the UVeditor
            area.spaces.active.cursor_location = err.data   # set cursor location

    print("Displaying error " + str(err))

def debugPreMapping(no_connection):
    rows, cols = numpy.where(model.CONNECTION_RESULTS[no_connection]['c'] == -1)
    neuronIDs = numpy.unique(rows)
    logger.info("Checking pre mapping " + str(model.CONNECTIONS[no_connection][0][0].name) + " -> " + str(model.CONNECTIONS[no_connection][0][-1].name))
    if len(neuronIDs):
        logger.info(str(len(neuronIDs)) + " neurons unconnected")
        for neuronID in neuronIDs:
            logger.info("Pre-index: " + str(neuronID))
            debugPreNeuron(no_connection, neuronID)
    else:
        logger.info("No unconnected neurons")

def debugPreNeuron(no_connection, pre_index):
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
        logger.info("Layer: " + str(s))
        logger.info("   pre_p3d: " + str(pre_p3d))
        logger.info("   pre_p2d: " + str(pre_p2d))
        logger.info("   pre_d: " + str(pre_d))

def debugPostMapping(no_connection):
    layers = model.CONNECTIONS[no_connection][0]
    neuronset1 = model.CONNECTIONS[no_connection][1]
    neuronset2 = model.CONNECTIONS[no_connection][2]
    slayer = model.CONNECTIONS[no_connection][3]
    connections = model.CONNECTIONS[no_connection][4]
    distances = model.CONNECTIONS[no_connection][5]

    neuronIDs = []

    logger.info("Checking post mapping " + str(model.CONNECTIONS[no_connection][0][0].name) + " -> " + str(model.CONNECTIONS[no_connection][0][-1].name))

    for i in range(0, len(layers[-1].particle_systems[neuronset2].particles)):
        post_p3d, post_p2d, post_d = pam.computeMapping(layers[:(slayer - 1):-1],
                                                    connections[:(slayer - 1):-1],
                                                    distances[:(slayer - 1):-1],
                                                    layers[-1].particle_systems[neuronset2].particles[i].location)
        if post_p3d is None:
            neuronIDs.append(i)
    if len(neuronIDs):
        logger.info(str(len(neuronIDs)) + " neurons unconnected")
    else:
        logger.info("No unconnected neurons")

    for neuronID in neuronIDs:
        logger.info("Post-index: " + str(neuronID))
        debugPostNeuron(no_connection, neuronID)

def debugPostNeuron(no_connection, post_index):
    layers = model.CONNECTIONS[no_connection][0]
    neuronset1 = model.CONNECTIONS[no_connection][1]
    neuronset2 = model.CONNECTIONS[no_connection][2]
    slayer = model.CONNECTIONS[no_connection][3]
    connections = model.CONNECTIONS[no_connection][4]
    distances = model.CONNECTIONS[no_connection][5]
    for s in range(len(layers) - 1, slayer, -1):
        post_p3d, post_p2d, post_d = pam.computeMapping(layers[:s-2:-1],
                                                        connections[:s-2:-1],
                                                        distances[:s-2:-1],
                                                        layers[-1].particle_systems[neuronset2].particles[post_index].location,
                                                        debug = True)
        logger.info("Layer: " + str(s))
        logger.info("   post_p3d: " + str(post_p3d))
        logger.info("   post_p2d: " + str(post_p2d))
        logger.info("   post_d: " + str(post_d))