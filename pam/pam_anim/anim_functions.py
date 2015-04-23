import numpy

# CONSTANTS
TAU = 20


# TODO(SK): Rephrase docstring and parameters/return value
# TODO(SK): Maybe this function should be renamed to mixLayerColors
def mixLayerValues(layerValue1, layerValue2):
    """Function that is called when a spike hits a neuron and the two layer
    values need to be mixed together

    :param dict layerValues1: values (???) of the given neuron
    :param dict layerValues2: values (???) for the incoming spike

    :return: mixed colors
    :rtype: dict

    """
    newValue = {"blue": 0.0, "red": 0.0, "green": 0.0}

    newValue["blue"] = (layerValue1["blue"] + layerValue2["blue"]) / 2
    newValue["red"] = (layerValue1["red"] + layerValue2["red"]) / 2
    newValue["green"] = (layerValue1["green"] + layerValue2["green"]) / 2

    return newValue


# TODO(SK): Rephrase docstring and parameters/return value
def decay(value, delta):
    """Calculate decay of a given value for a color in a neuron

    :param float value: color value (???)
    :param float delta: time since the last update for this neuron in ms

    :return: A new value (???)
    :rtype: float

    """

    return value * numpy.exp(-delta / TAU)


def getInitialColorValues(neuronGroupID, neuronID, neuronGroups):
    """Return an initial value (???) to a neuron when an update is called
    the first time

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
    if neuronID % 2 == 0:
        layerValue["blue"] = 1.0
    else:
        layerValue["red"] = 1.0
    return layerValue


# TODO(SK): Rephrase note to be short an precise, give things proper names rather
# TODO(SK): than speaking of "values": e.g. colors, input_value, spike_delay, etc
# TODO(SK): Please try to wrap code and docstrings at 80 characters
# TODO(SK): Why are obsolete things documented?
def applyColorValues(layerValues, neuronID, neuronGroupID, neuronGroups):
    """Apply a color to a spike object

    :param bpy.types.Object obj: an object

    .. note::

        Following parameters are obsolete:

            * layerValues: Dictionary containing all the color information.
              The float values are not guaranteed to haveany boundaries and
              may have to be normalized.
            * neuronID: The ID of the neuron this spike is originating from
            * neuronGroupID: The ID of the neuron group
            * neuronGroups: A list of all neuron groups available. Every entry
              in this list is an object with the following properties:
                * name
                * particle_system,
                * count
                * areaStart
                * areaEnd
                * connections

        See data.py for a detailed description.
    :return float[4]: the color for this spike

    """
    red = layerValues["red"]
    blue = layerValues["blue"]
    green = layerValues["green"]

    return (red, green, blue, 1.0)
