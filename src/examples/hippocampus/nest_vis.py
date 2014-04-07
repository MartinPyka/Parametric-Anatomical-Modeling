# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:08:03 2014

Visualized data, imported from PAM for NEST

@author: martin
"""

import numpy as np

def connectivityMatrix(connections, pre_num, post_num):
    """ Creates a pre_num x post_num connection matrix for the given 
    connetions array, which is pre_num x synapse_numbers
    
    connections     : pre_num x synapse_numbers matrix
    pre_num         : number of pre-synaptic neurons
    post_num        : number of post-synaptic neurons
    
    Returns:

        result      : pre_num x post_num matrix
    """
    
    result = np.zeros((pre_num, post_num))
    for i, row in enumerate(connections):
        for c in row:
            result[i, c] = 1
        
    return result