import numpy
import zipfile
import io
import os
import csv
from bpy.path import abspath

from .. import model

DELAYS = []
TIMINGS = []

# TODO(SK): Missing docstring
def csv_read(data):
    reader = csv.reader(data, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    return [row for row in reader]


# TODO(SK): Refactor, in general global variables are ugly and fault prone.
SUPPORTED_FILETYPES = {
    ".csv": csv_read
}


# TODO(SK): Missing docstring
def csvfile_read(filename):
    f = open(filename, 'r')
    result = csv_read(f)
    f.close()
    return result


# TODO(SK): Missing docstring
def readModelData(connectionsPath):
        # Convert the Blender specific paths to absolute paths
    connectionsPath = abspath(connectionsPath)

    # result is a tuple of two lists (data + filenames)
    result = import_model_from_zip(connectionsPath)

    # NeuronGroup Objects (name, particles, count, areaStart)
    neuronGroups = []
    i = 0
    for n in result[0][result[1].index('neurongroups')]:
        neuronGroups.append(NeuronGroup(n[0], n[1], int(n[2]), int(i)))
        i += n[2]

    # connections between neuron layers
    maxConnectionFiles = 0
    for c in result[0][result[1].index('connections')]:
        connectionID = int(c[0])
        groupFrom = int(c[1])
        groupTo = int(c[2])
        neuronGroups[groupFrom].connections.append((connectionID, groupFrom, groupTo))

        if connectionID > maxConnectionFiles:
            maxConnectionFiles = connectionID

    # neuron connections
    connections = []
    for i in range(maxConnectionFiles + 1):
        c_elem = result[0][result[1].index(str(i) + "_c")]
        c_elem = [[int(x) for x in i] for i in c_elem]
        d_elem = result[0][result[1].index(str(i) + "_d")]
        connections.append({'c': numpy.array(c_elem), 'd': numpy.array(d_elem)})

    global NEURON_GROUPS
    global CONNECTIONS
    NEURON_GROUPS = neuronGroups
    CONNECTIONS = connections


# TODO(SK): Missing docstring
def readSimulationData(simulationFile):
    # Open timing file (output.csv)
    neuronTimingPath = abspath(simulationFile)
    timingFile = open(neuronTimingPath, 'r')
    # read the data into the TIMINGS variable
    global TIMINGS
    timing_data = csv_read(timingFile)
    TIMINGS = [(int(row[0]), int(row[1]), float(row[2])) for row in timing_data]
    timingFile.close()

    prefix = neuronTimingPath[:-4]
    global DELAYS
    try:
        for i in range(0, len(model.CONNECTIONS)):
            DELAYS.append(csvfile_read(prefix + '_d' + str(i) + '.csv'))
    except:
        print('cannot find file: ' + prefix + '_d' + str(i) + '.csv')
