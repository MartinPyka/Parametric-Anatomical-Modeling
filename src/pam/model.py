"""Data model module"""

import pickle
import copy

NG_LIST = []
NG_DICT = {}
CONNECTION_COUNTER = 0
CONNECTION_INDICES = []
CONNECTIONS = []
CONNECTION_RESULTS = []


def convertObject2String(connection):
    """ Takes a CONNECTION-struct and converts bpy.objects to 
    string names and returns a list of stirngs """
    return [o.name for o in connection[0]]

def makeConnectionPickleReady(connections):
    result = []
    for c in connections:
        new_c = (convertObject2String(c))
        new_c = new_c + c[1:]
        result.append(new_c)
    return result

def convertVector2Array(connection_results):
    """ Takes a CONNECTION_RESULTS-struct and converts mathutils.Vectors
    to numpy.arrays and returns them """
    result = []
    for c in connection_results:
        result.append(numpy.array(c['s']))
    return result



# TODO(SK): missing docstring
class ModelSnapshot(object):
    def __init__(self):
        self.NG_LIST = NG_LIST
        self.NG_DICT = NG_DICT
        self.CONNECTION_COUNTER = CONNECTION_COUNTER
        self.CONNECTION_INDICES = CONNECTION_INDICES
        self.CONNECTIONS = copy.deepcopy(CONNECTIONS)
        self.CONNECTION_RESULTS = copy.deepcopy(CONNECTION_RESULTS)


# TODO(SK): missing docstring
def save_snapshot(path):
    snapshot = ModelSnapshot()
    pickle.dump(snapshot, open(path, "wb"))


# TODO(SK): missing docstring
def load_snapshot(path):
    snapshot = pickle.load(open(path, "rb"))
    return snapshot
