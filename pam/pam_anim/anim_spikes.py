import logging

import csv
import bpy

from pam import model
from . import data
from . import helper

logger = logging.getLogger(__package__)

ANIM_SPIKE_SCALE = 15.0
ANIM_SPIKE_FADEOUT = 5


def readSpikeData(filename):
    """ Read spike-data from a csv-file and returns them as list
    """
    file = open(filename, 'r')

    reader = csv.reader(file, delimiter=";")
    data = [row for row in reader]

    file.close()
    return data


def generateLayerNeurons(layer, particle_system):
    """ Generates for each particle (neuron) a cone with appropriate
    naming """
    # generate first mesh
    i = 0
    p = layer.particle_systems[particle_system].particles[0]
    bpy.ops.mesh.primitive_cone_add(
        vertices=3,
        radius1=0.01,
        radius2=0,
        depth=0.02,
        location=p.location,
        layers=bpy.context.scene.layers
    )
    cone = bpy.context.active_object
    cone.name = 'n' + '_' + layer.name + '_' + '%05d' % i
    cone.data.materials.append(layer.data.materials[0])

    # generates linked duplicates of this mesh
    for i, p in enumerate(layer.particle_systems[particle_system].particles[1:]):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = cone
        bpy.context.object.select = True

        bpy.ops.object.duplicate(linked=True, mode='INIT')
        dupli = bpy.context.active_object
        dupli.name = 'n' + '_' + layer.name + '_' + '%05d' % (i + 1)
        dupli.location = p.location


def generateNetworkNeurons():
    for neurongroup in model.NG_LIST:
        layer = bpy.data.objects[neurongroup[0]]
        print(layer.name)
        particle_system = neurongroup[1]
        generateLayerNeurons(layer, particle_system)


def animNeuronSpiking(func):

    timings = data.TIMINGS
    neuronGroups = data.NEURON_GROUPS

    logger.info('Animate spiking data')
    for neuronIDinGroup, neuronGroupID, fireTime in timings:
        layer_name = neuronGroups[neuronGroupID].name
        frame = helper.projectTimeToFrames(fireTime)
        func(layer_name, neuronIDinGroup, frame)


def animNeuronScaling(layer_name, n_id, frame):
    """ Animate neuron spiking for a given neuron defined by
    layer_name, neuron-id and a given frame """
    neuron = bpy.data.objects['n_' + layer_name + '_%05d' % n_id]

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = neuron
    bpy.context.object.select = True

    # define the animation
    bpy.context.scene.frame_set(frame=frame - 1)
    bpy.ops.anim.keyframe_insert_menu(type='Scaling')
    bpy.context.scene.frame_set(frame=frame + helper.timeToFrames(ANIM_SPIKE_FADEOUT))
    bpy.ops.anim.keyframe_insert_menu(type='Scaling')
    bpy.context.scene.frame_set(frame=frame)
    neuron.scale = (ANIM_SPIKE_SCALE, ANIM_SPIKE_SCALE, ANIM_SPIKE_SCALE)
    bpy.ops.anim.keyframe_insert_menu(type='Scaling')


def deleteNeurons():
    """ delete all objects with the prefix n_
    """
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern='n_*')
    bpy.ops.object.delete(use_global=False)
