"""Data model module"""

import pickle

import bpy
import bpy_extras
import mathutils
import numpy

NG_LIST = []
NG_DICT = {}
CONNECTION_COUNTER = 0
CONNECTION_INDICES = []
CONNECTIONS = []
CONNECTION_RESULTS = []


def convertObject2String(connection):
    """Takes a CONNECTION-struct and converts bpy.objects to
    string names and returns a list of strings"""
    return [o.name for o in connection[0]]


def convertString2Object(connection):
    """Takes a CONNECTION-struct and converts string names to
    bpy.objects and returns a list of bpy.objects"""
    return [bpy.data.objects[name] for name in connection[0]]


def Connection2Pickle(connections):
    result = []
    for c in connections:
        new_c = [convertObject2String(c)]
        new_c = new_c + list(c[1:])
        result.append(new_c)
    return result


def Pickle2Connection(connections):
    result = []
    for c in connections:
        new_c = [convertString2Object(c)]
        new_c = new_c + list(c[1:])
        result.append(new_c)
    return result


def convertVector2Array(connection_results):
    """ Takes a CONNECTION_RESULTS-struct and converts mathutils.Vectors
    to numpy.arrays and returns them """
    result = []
    for c in connection_results:
        temp = []
        for r in c['s']:
            temp.append(numpy.array(r))
        result.append({'c': c['c'], 'd': c['d'], 's': temp})
    return result


def convertArray2Vector(connection_results):
    """ Takes a CONNECTION_RESULTS-struct and converts numpy.arrays
    to mathutils.Vector and returns them """
    result = []
    for c in connection_results:
        temp = []
        for r in c['s']:
            if r.size > 0:
                temp.append([mathutils.Vector(v) for v in r])
            else:
                temp.append([[] for i in range(r.shape[0])])
        result.append({'c': c['c'], 'd': c['d'], 's': temp})
    return result


# TODO(SK): missing docstring
class ModelSnapshot(object):
    def __init__(self):
        global NG_LIST
        global NG_DICT
        global CONNECTION_COUNTER
        global CONNECTION_INDICES
        global CONNECTIONS
        global CONNECTION_RESULTS
        self.NG_LIST = NG_LIST
        self.NG_DICT = NG_DICT
        self.CONNECTION_COUNTER = CONNECTION_COUNTER
        self.CONNECTION_INDICES = CONNECTION_INDICES
        self.CONNECTIONS = Connection2Pickle(CONNECTIONS)
        self.CONNECTION_RESULTS = convertVector2Array(CONNECTION_RESULTS)

    def __eq__(self, other):
        return str(self.__dict__) == str(other.__dict__)


def save(path):
    """ saves the current model using pickle in the given path """
    snapshot = ModelSnapshot()
    pickle.dump(snapshot, open(path, "wb"))


# TODO(SK): missing docstring
def load(path):
    """ loads the model with pickle from the given path """
    snapshot = pickle.load(open(path, "rb"))
    return snapshot


def compare(path1, path2):
    """ compares two models with each other, addressed by path1 and
    path """
    m1 = load(path1)
    m2 = load(path2)
    return m1 == m2


def reset():
    """ Resets the most important variables without calculating everything from
    scratch """
    global NG_LIST
    global NG_DICT
    global CONNECTION_COUNTER
    global CONNECTION_INDICES
    global CONNECTIONS
    global CONNECTION_RESULTS
    NG_LIST = []
    NG_DICT = {}
    CONNECTION_COUNTER = 0
    CONNECTION_INDICES = []
    CONNECTIONS = []
    CONNECTION_RESULTS = []


class PAMModelLoad(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Model Load Operator"""

    bl_idname = "pam.model_load"
    bl_label = "Load model data"
    bl_description = "Load model data"

    def execute(self, context):
        snapshot = load(self.filepath)

        global NG_LIST
        global NG_DICT
        global CONNECTION_COUNTER
        global CONNECTION_INDICES
        global CONNECTIONS
        global CONNECTION_RESULTS

        NG_LIST = snapshot.NG_LIST
        NG_DICT = snapshot.NG_DICT
        CONNECTION_COUNTER = snapshot.CONNECTION_COUNTER
        CONNECTION_INDICES = snapshot.CONNECTION_INDICES
        CONNECTIONS = Pickle2Connection(snapshot.CONNECTIONS)
        CONNECTION_RESULTS = convertArray2Vector(snapshot.CONNECTION_RESULTS)

        return {'FINISHED'}


class PAMModelSave(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Model Save Operator"""

    bl_idname = "pam.model_save"
    bl_label = "Save model data"
    bl_description = "Save model data"

    filename_ext = ".pam"

    @classmethod
    def poll(cls, context):
        return any(CONNECTIONS)

    def execute(self, context):
        save(self.filepath)

        return {'FINISHED'}
