import bpy

import numpy
from .. import pam

# CONSTANTS
TAU = 20


def mixLabels(layerValue1, layerValue2):
    """Function that is called when a spike hits a neuron and the two 
    labels need to be mixed together

    :param dict layerValues1: label of the given neuron
    :param dict layerValues2: label for the incoming spike

    :return: mixed colors
    :rtype: dict

    """
    newValue = {"blue": 0.0, "red": 0.0, "green": 0.0}

    newValue["blue"] = (layerValue1["blue"] + layerValue2["blue"]) / 2
    newValue["red"] = (layerValue1["red"] + layerValue2["red"]) / 2
    newValue["green"] = (layerValue1["green"] + layerValue2["green"]) / 2

    return newValue


def decay(value, delta):
    """Calculate decay of a given label value in a neuron

    :param float value: label value
    :param float delta: time since the last update for this neuron in ms

    :return: The new value after a decay has been applied
    :rtype: float

    """

    return value * numpy.exp(-delta / TAU)


def getInitialLabel(neuronGroupID, neuronID, neuronGroups):
    """Return an initial label for a neuron when an update is called
    for the first time

    :param int neuronGroupID: id of neuron group
    :param int neuronID: id of neuron
    :param list neuronGroups: all neuron groups

    .. note::
        Every entry in `neuronGroups` is an object with the following properties:
            * name
            * particle_system
            * count
            * areaStart
            * areaEnd
            * connections

        See data.py for a detailed description

    :return: color values
    :rtype: dict

    """
    ng = neuronGroups[neuronGroupID]

    layerValue = {"blue": 0.0, "red": 0.0, "green": 0.0}
    if (neuronID + neuronGroupID) % 2 == 0:
        layerValue["blue"] = 1.0
    else:
        layerValue["red"] = 1.0
    return layerValue

def labelToColor(layerValues, neuronID, neuronGroupID, neuronGroups):
    """Apply a color to a spike object from a given label

    :param layerValues: The label for this spike.
    :type layerValues: dict
    :param neuronID: The ID of the neuron this spike is originating from
    :type neuronID: int
    :param neuronGroupID: The ID of the neuron group
    :type neuronGroupID: int
    :param neuronGroups: A list of all neuron groups available. Every entry
      in this list is an object with the following properties:
        * name
        * particle_system,
        * count
        * areaStart
        * areaEnd
        * connections

        See data.py for a detailed description.
    :return: the color for this spike
    :rtype:  float[4]

    """
    red = layerValues["red"]
    blue = layerValues["blue"]
    green = layerValues["green"]

    return (red, green, blue, 1.0)

def getInitialLabelMask(neuronGroupID, neuronID, neuronGroups):
    """Checks if a neuron is inside or outside of the mask, and returns
    a color label.

    :param neuronID: The ID of the neuron this spike is originating from
    :type neuronID: int
    :param neuronGroupID: The ID of the neuron group
    :type neuronGroupID: int
    :param neuronGroups: A list of all neuron groups available. Every entry
      in this list is an object with the following properties:
        * name
        * particle_system,
        * count
        * areaStart
        * areaEnd
        * connections

        See data.py for a detailed description.
    :return: The label for this spike
    :rtype:  dict
    """
    maskObject = bpy.data.objects[bpy.context.scene.pam_anim_material.maskObject]
    insideMaskColor = bpy.context.scene.pam_anim_material.insideMaskColor
    outsideMaskColor = bpy.context.scene.pam_anim_material.outsideMaskColor
    neuron_group = neuronGroups[neuronGroupID]
    layer_name = neuron_group[0]
    particle_system_name = neuron_group[1]
    particle = bpy.data.objects[layer_name].particle_systems[particle_system_name].particles[neuronID]
    if pam.checkPointInObject(maskObject, particle.location):
        return {"red": insideMaskColor[0], "green": insideMaskColor[1], "blue": insideMaskColor[2]}
    else:
        return {"red": outsideMaskColor[0], "green": outsideMaskColor[1], "blue": outsideMaskColor[2]}
