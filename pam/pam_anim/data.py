import numpy
import zipfile
import io
import os
import csv
import bpy
from bpy.path import abspath
from bpy.path import display_name_from_filepath

from .. import model

DELAYS = []
TIMINGS = []
noAvailableConnections = 0

# TODO(SK): Missing docstring
def csv_read(data):
    reader = csv.reader(data, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    return [row for row in reader if len(row) > 0]


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
def import_model_from_zip(filepath):
    result = {}
    with zipfile.ZipFile(filepath, "r", zipfile.ZIP_DEFLATED) as file:
        for filename in file.namelist():
            filename_split = os.path.splitext(filename)
            filename_extension = filename_split[-1]
            data = io.StringIO(str(file.read(filename), 'utf-8'))
            func = SUPPORTED_FILETYPES[filename_extension]
            matrix = func(data)
            result[filename_split[0]] = (matrix)
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
    fileName = display_name_from_filepath(simulationFile)
    timingZip = import_model_from_zip(neuronTimingPath)
    
    # read the data into the TIMINGS variable
    global TIMINGS
    TIMINGS = []
    timing_data = timingZip[fileName]

    for row in timing_data:
        if len(row) == 3:
            
            # if start time point is not reached, simply continue
            if (float(row[2]) < bpy.context.scene.pam_anim_animation.startTime):
                continue
            
            # only load data up to the prespecified time point
            if (float(row[2]) < bpy.context.scene.pam_anim_animation.endTime):
                TIMINGS.append((int(row[0]), int(row[1]), float(row[2])))
            else:
                break

    global DELAYS
    DELAYS = []
    try:
        for i in range(0, len(model.CONNECTIONS)):
            DELAYS.append(timingZip[fileName + "_d" + str(i)])
    except:
        print('cannot find file: ' + fileName + '_d' + str(i) + '.csv')
    
    DELAYS = numpy.array(DELAYS)
    global noAvailableConnections
    noAvailableConnections = len(DELAYS[0][0])