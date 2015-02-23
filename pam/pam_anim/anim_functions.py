import numpy

# CONSTANTS
TAU = 20


def mixLayerValues(layerValue1, layerValue2):
        """Function that is called when a spike hits a neuron and the two layer values need to be mixed together.

        :param layerValues1: Dictionary with keys defined in getInitialColorValues() and float values.
                This are the values of the given neuron
        :param layerValues2: See layerValues1, but gives the values for the incoming spike

        :returns: The mixed values as a dictionary. Does not need to contain
                the same keys as the incoming dictionaries
        """
        newValue = {"blue": 0.0, "red": 0.0, "green": 0.0}

        newValue["blue"] = (layerValue1["blue"] + layerValue2["blue"]) / 2
        newValue["red"] = (layerValue1["red"] + layerValue2["red"]) / 2
        newValue["green"] = (layerValue1["green"] + layerValue2["green"]) / 2

        return newValue


def decay(value, delta):
        """Function for calculating the decay of a given value for a color in a neuron

        :param value: Float value from the layer dictionary from a single neuron
        :param delta: Time since the last update for this neuron as float in ms

        :returns: A new value"""

        return value * numpy.exp(-delta / TAU)


def getInitialColorValues(neuronGroupID, neuronID, neuronGroups):
        """Function for giving an initial value to a neuron when an update is called the first time

        :param neuronGroupID: The ID of the neuron group this neuron is a part of
        :param neuronID: The ID of the neuron
        :param neuronGroups: A list of all neuron groups available. Every entry in this list
                is an object with the following properties: name, particle_system, count,
                areaStart, areaEnd, connections.

        See data.py for a detailed description

        :returns: A dictionary with string keys and float values
        """
        ng = neuronGroups[neuronGroupID]

        layerValue = {"blue": 0.0, "red": 0.0, "green": 0.0}
        if neuronID % 2 == 0:
                layerValue["blue"] = 1.0
        else:
                layerValue["red"] = 1.0
        return layerValue


def applyColorValues(obj, layerValues, neuronID, neuronGroupID, neuronGroups):
        """Function for applying a color to a spike object

        :param obj: The blender object. Set obj.color to change the object color

        .. note::

                Following parameters are obsolete.

                * layerValues: Dictionary containing all the color information. The float
                        values are not guaranteed to haveany boundaries and may have to be normalized.
                * neuronID: The ID of the neuron this spike is originating from
                * neuronGroupID: The ID of the neuron group
                * neuronGroups: A list of all neuron groups available. Every entry in
                        this list is an object with the following properties: name, particle_system,
                        count, areaStart, areaEnd, connections.

        See data.py for a detailed description
        """
        red = layerValues["red"]
        blue = layerValues["blue"]
        green = layerValues["green"]

        obj.color = (red, green, blue, 1.0)
