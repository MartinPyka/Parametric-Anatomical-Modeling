"""Data model module"""

import pickle

import bpy
import bpy_extras
import mathutils
import numpy

from .utils import quadtree

NG_LIST = []
NG_DICT = {}
CONNECTION_COUNTER = 0
CONNECTION_INDICES = []
CONNECTIONS = []
CONNECTION_RESULTS = []
CONNECTION_ERRORS = []

QUADTREE_CACHE = {}

def getPreIndicesOfPostIndex(c_index, post_index ):
    """ returns for a given connection-index c_index and a given post-synaptic
    neuron post_index the row-indices (index of the pre-synaptic neurons) and the
    column-index (for identifying the synapse """
    pre_indices, synapses = numpy.where(numpy.array(CONNECTION_RESULTS[c_index]['c']) == post_index)
    return pre_indices, synapses

# TODO(SK): Fill in docstring parameter/return values
def convertObject2String(connection):
    """Takes a CONNECTION-struct and converts `bpy.objects` to
    string names and returns a list of strings

    :param list connection:
    :return:
    :rtype:

    """
    return [o.name for o in connection[0]]


# TODO(SK): Fill in docstring parameter/return values
def convertString2Object(connection):
    """Takes a CONNECTION-struct and converts string names to
    `bpy.objects` and returns a list of `bpy.objects`

    :param list connection:
    :return:
    :rtype:

    """
    return [bpy.data.objects[name] for name in connection[0]]


# TODO(SK): Fill in docstring parameter/return values
def Connection2Pickle(connections):
    """

    :param list connection:
    :return:
    :rtype:

    """
    result = []
    for c in connections:
        new_c = [convertObject2String(c)]
        new_c = new_c + list(c[1:])
        new_c[6] = c[6].__name__
        new_c[8] = c[8].__name__
        result.append(new_c)
    return result


# TODO(SK): Fill in docstring parameter/return values
def Pickle2Connection(connections):
    """

    :param list connection:
    :return:
    :rtype:

    """
    result = []
    for c in connections:
        new_c = [convertString2Object(c)]
        new_c = new_c + list(c[1:])
        result.append(tuple(new_c))
    return result


# TODO(SK): Fill in docstring parameter/return values
def convertVector2Array(connection_results):
    """Takes a CONNECTION_RESULTS-struct and converts `mathutils.Vector`
    to `numpy.Array`

    :param list connection_results:
    :return:
    :rtype:

    """
    result = []
    for c in connection_results:
        temp = []
        for r in c['s']:
            temp.append(numpy.array(r))
        result.append({'c': c['c'], 'd': c['d'], 's': temp})
    return result


# TODO(SK): Fill in docstring parameter/return values
def convertArray2Vector(connection_results):
    """Takes a CONNECTION_RESULTS-struct and converts `numpy.array`
    to `mathutils.Vector`

    :param list connection_results:
    :return:
    :rtype:

    """
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

def createModelSnapshot():
    global NG_LIST
    global NG_DICT
    global CONNECTION_COUNTER
    global CONNECTION_INDICES
    global CONNECTIONS
    global CONNECTION_RESULTS
    l = []
    l.append(NG_LIST)
    l.append(NG_DICT)
    l.append(CONNECTION_COUNTER)
    l.append(CONNECTION_INDICES)
    l.append(Connection2Pickle(CONNECTIONS))
    return l

def save(path):
    """Save current model via pickle to given path

    :param str path: filepath

    """
    snapshot = createModelSnapshot()
    pickle.dump(snapshot, open(path, "wb"))


def load(path):
    """Load model via pickle from given path

    :param str path: filepath

    """
    snapshot = pickle.load(open(path, "rb"))

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
    CONNECTION_ERRORS = []


def compare(path1, path2):
    """Compare two models with each other

    :param str path1: a path
    :param str path2: another path

    """
    m1 = load(path1)
    m2 = load(path2)
    return m1 == m2


def reset():
    """Reset most important variables"""
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
    CONNECTION_ERRORS = []
    clearQuadtreeCache()

def clearQuadtreeCache():
    """Clears the quadtree cache. 
    Has to be called each time a uv-map has changed."""
    global QUADTREE_CACHE
    QUADTREE_CACHE = {}

class PAMModelLoad(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a model"""

    bl_idname = "pam.model_load"
    bl_label = "Load model data"
    bl_description = "Load model data"

    def execute(self, context):
        load(self.filepath)

        return {'FINISHED'}


class PAMModelSave(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save current model"""

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
