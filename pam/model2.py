"""Model data module"""

import os

CURRENT = None
PAST = []


class Network(object):
    """Network model data"""

    def __init__(self):
        pass

    def __str__(self):
        pass

    def __eq__(self, other):
        """Checks equality

        Example:
            m = Model()
            b = Model()
            a == b

        Result:
            bool
        """
        return (isinstance(other, self.__class__)) and \
            (self.__dict__ == other.__dict__)

    def __ne__(self, other):
        """Checks for inequality"""
        return not self.__eq__(other)

    def __bool__(self):
        pass

    def __len__(self):
        """Return length of Model

        Example:
            m = Model()
            len(m)

        Result:
            int
        """
        pass

    def __contains__(self, item):
        """Checks if model conains an object

        Example:
            m = Model()
            t = Object()
            t in m

        Result:
            bool
        """
        pass

    # Pickle API

    def __getnewargs__(self):
        pass

    def __getstate__(self):
        pass

    def setstate__(self, state):
        pass


class Neuron(object):
    """Neuron representation"""

    def __init__(self):
        pass


def load_network(filepath):
    return pickle.load(open(filepath), "rb")


def dump_network(filepath, model=None):
    to_dump = CURRENT

    if model and isinstance(model, Network):
        to_dump = model

    pickle.dump(to_dump, open(filepath, "wb"))


def dump_all_network(path, prefix):
    dump_network(path, "_".join(prefix, "current"))
    for i, network in enumerate(PAST):
        dump_network(path, "_".join(prefix, "past", str(i)))


def reset():
    global CURRENT, PAST
    PAST.append(current)
    CURRENT = Network()
