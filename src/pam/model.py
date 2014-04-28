"""Data model module"""

import pickle

NG_LIST = []
NG_DICT = {}
CONNECTION_COUNTER = 0
CONNECTION_INDICES = []
CONNECTIONS = []
CONNECTION_RESULTS = []


# TODO(SK): missing docstring
class ModelSnapshot(object):
    def __init__(self):
        self.NG_LIST = NG_LIST
        self.NG_DICT = NG_DICT
        self.CONNECTION_COUNTER = CONNECTION_COUNTER
        self.CONNECTION_INDICES = CONNECTION_INDICES
        self.CONNECTIONS = CONNECTIONS
        self.CONNECTION_RESULTS = CONNECTION_RESULTS


# TODO(SK): missing docstring
def save_snapshot(path):
    snapshot = ModelSnapshot()
    pickle.dump(snapshot, open(path, "wb"))


# TODO(SK): missing docstring
def load_snapshot(path):
    snapshot = pickle.load(open(path, "rb"))
    return snapshot
