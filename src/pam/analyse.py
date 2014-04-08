# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 14:54:53 2014

@author: martin
"""

import collections
import numpy as np
import pickle


def flatten(x):
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]


def loadDistanceData(filename):
    """ Loads a file with distance data
    filename        : name of the file to be loaded

    Return:
        data        : data[0], connection distance
                      data[1], surface distance
    """
    f = open(filename, 'rb')
    data = pickle.load(f)
    f.close()

    d = data[0]
    rd = data[1]

    d = np.array(d)
    rd = np.array(rd)

    return d, rd
