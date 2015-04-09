import logging

import csv
import bpy

from pam import model
from . import data
from . import helper

logger = logging.getLogger(__package__)

# TODO(SK): Missing docstring
def readSpikeData(filename):
    """Read spike-data from a csv-file and returns them as list"""
    file = open(filename, 'r')

    reader = csv.reader(file, delimiter=";")
    data = [row for row in reader]

    file.close()
    return data


# TODO(SK): Fill in docstring parameters/return values
def generateLayerNeurons(layer, particle_system, obj, object_color=[],
                         indices=-1):
    """Generates for each particle (neuron) a cone with appropriate naming"""
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

        elif bpy.context.scene.pam_anim_mesh.spikeUseLayerColor:
            dupli.color = layer.color

        else:
            dupli.color = bpy.context.scene.pam_anim_mesh.spikeColor


# TODO(SK): Missing docstring
def generateNetworkNeurons(obj):
    for neurongroup in model.NG_LIST:
        layer = bpy.data.objects[neurongroup[0]]
        print(layer.name)
        particle_system = neurongroup[1]
        generateLayerNeurons(layer, particle_system, obj)


# TODO(SK): Missing docstring
def animNeuronSpiking(func):
    timings = data.TIMINGS
    neuronGroups = data.NEURON_GROUPS

    no_timings = len(timings)

    logger.info('Animate spiking data')
    for i, (neuronIDinGroup, neuronGroupID, fireTime) in enumerate(timings):
        logger.info(str(i) + "/" + str(no_timings))

        layer_name = neuronGroups[neuronGroupID].name
        frame = helper.projectTimeToFrames(fireTime)
        func(layer_name, neuronIDinGroup, frame)


# TODO(SK): Fill in docstring parameters/return values
def animNeuronScaling(layer_name, n_id, frame):
    """Animate neuron spiking for a given neuron defined by
    layer_name, neuron-id and a given frame"""
    neuron = bpy.data.objects['n_' + layer_name + '_%05d' % (n_id + 1)]

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = neuron
    bpy.context.object.select = True

    # define the animation
    animSpikeScale = bpy.context.scene.pam_anim_mesh.spikeScale
    animSpikeFadeout = bpy.context.scene.pam_anim_mesh.spikeFadeout

    bpy.context.scene.frame_set(frame=frame - 1)
    bpy.ops.anim.keyframe_insert_menu(type='Scaling')
    bpy.context.scene.frame_set(frame=frame + animSpikeFadeout)
    bpy.ops.anim.keyframe_insert_menu(type='Scaling')
    bpy.context.scene.frame_set(frame=frame)
    neuron.scale = (animSpikeScale, animSpikeScale, animSpikeScale)
    bpy.ops.anim.keyframe_insert_menu(type='Scaling')


# TODO(SK): Rephrase docstring, purpose?
def deleteNeurons():
    """Delete all objects with the prefix `n_`"""
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern='n_*')
    bpy.ops.object.delete(use_global=False)
