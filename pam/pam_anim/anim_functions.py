import numpy

# CONSTANTS
TAU = 20


def mixLayerValues(layerValue1, layerValue2):
        """Function that is called when a spike hits a neuron and the two layer values
        need to be mixed together.
        layerValues1:      Dictionary with keys defined in getInitialColorValues() and float values.
                           This are the values of the given neuron
        layerValues2:      See layerValues1, but gives the values for the incoming spike
        -------------------
        return:            The mixed values as a dictionary. Does not need to contain the same keys as the incoming dictionaries
        """
        newValues = {}
        for key in layerValue1:
                if key in layerValue2:
                        newValues[key] = layerValue1[key] + layerValue2[key]
                else:
                        newValues[key] = layerValue1[key]

        for key in layerValue2:
                if key not in layerValue1:
                        newValues[key] = layerValue2[key]

        return newValues


def decay(value, delta):
        """Function for calculating the decay of a given value for a color in a neuron

        value:              Float value from the layer dictionary from a single neuron
        delta:              Time since the last update for this neuron as float in ms
        --------------------
        return:             A new value"""

        return value * numpy.exp(-delta / TAU)


def getInitialColorValues(neuronGroupID, neuronID, neuronGroups):
        """Function for giving an initial value to a neuron when an update is called the first time
        neuronGroupID:      The ID of the neuron group this neuron is a part of
        neuronID:           The ID of the neuron
        neuronGroups:       A list of all neuron groups available. Every entry in this list is an object
                            with the following properties: name, particle_system, count, areaStart, areaEnd, connections.
                            See data.py for a detailed description
        --------------------
        return:             A dictionary with string keys and float values
        """
        ng = neuronGroups[neuronGroupID]

        layerValue = {}
        if neuronID % 2 == 0:
                layerValue["blue"] = 1.0
        else:
                layerValue["red"] = 1.0
        return layerValue


def applyColorValues(obj, layerValues, neuronID, neuronGroupID, neuronGroups):
        """Function for applying a color to a spike object
        obj:                The blender object. Set obj.color to change the object color
        layerValues:        Dictionary containing all the color information. The float values are not guaranteed to have
                            any boundaries and may have to be normalized.
        neuronID:           The ID of the neuron this spike is originating from
        neuronGroupID:      The ID of the neuron group
        neuronGroups:       A list of all neuron groups available. Every entry in this list is an object
                            with the following properties: name, particle_system, count, areaStart, areaEnd, connections.
                            See data.py for a detailed description
        """
        col1 = (1.0, 0.1, 0.1)
        col2 = (0.5, 0.6, 0.8)

        if "blue" in layerValues:
                red = col1[0]
                green = col1[1]
                blue = col1[2]
        else:
                red = (0.9 * col1[0] - 0.1 * col2[0])
                green = (0.9 * col1[1] - 0.1 * col2[1])
                blue = (0.9 * col1[2] - 0.1 * col2[2])

                # Prevent black spikes. Do not use random numbers here since
                # spikes of the same type would be colored differently
                if red < 0.1 and green < 0.1 and blue < 0.1:
                        red += (col1[0] * 0.7)
                        green += (col1[1] * 0.5)
                        blue += (col1[2] * 0.4)

        obj.color = (red, blue, green, 1.0)
