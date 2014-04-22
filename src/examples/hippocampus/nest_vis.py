# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:08:03 2014

Visualized data, imported from PAM for NEST

@author: martin
"""

import numpy as np
import matplotlib.pyplot as mp


def plotDelayHistograms(m):
    
    for i, d in enumerate(m['d']):
        mp.figure()
        c = np.array(d)
        c = c.flatten()
        print(c.var())
        mp.hist(c[c>0], 20)    
        mp.title(m['neurongroups'][0][m['connections'][0][i][1]][0] + ' - ' +
                 m['neurongroups'][0][m['connections'][0][i][2]][0])
                 

def plotConnectionDelayHistogram(connections, m, neurons, bins):
    """ computes delay-histogram for a given connection-chain
    
    connections :    list of connections
    m           :    model-variable of the whole network
    """
    result = []
    for i in neurons:
        print(i)
        result = result + recursivelyComputeDelays(connections, m, i)
    
    mp.figure()
    mp.hist(result,bins)
    mp.title("Connection delays")        
    return result
    
    
def recursivelyComputeDelays(connections, m, neuron_number):
    """ computes recursively connectoin delays for all connections
    in the connections-list """
    result = []
    if (len(connections) == 1):
        for delay in m['d'][ connections[0][0] ][neuron_number]:
            result.append(delay)
        return result
    else:
        for i, delay in enumerate(m['d'][ connections[0][0] ][neuron_number]):
            if m['c'][ connections[0][0] ][neuron_number][i] == -1:
                continue
            
            post_neurons = recursivelyComputeDelays(
                connections[1::], 
                m, 
                m['c'][ connections[0][0] ][neuron_number][i])
            for post_neuron in post_neurons:
                result.append(delay + post_neuron)
                                
    return result
                 

def printConnections(m):
    """ Print all connection pairs in m """
    for i, c in enumerate(m['c']):
        print(m['neurongroups'][0][m['connections'][0][i][1]][0] + ' - ' +
              m['neurongroups'][0][m['connections'][0][i][2]][0])
              
def printNeuronGroups(m):
    """ Print all neurongroups """
    for ng in m['neurongroups'][0]:
        print(ng)
              
def getConnectionMatrix(m, c_index):
    """ Returns the full pre x post-neuron matrix for the connection
        with index c_index """
        
    matrix = connectivityMatrix(
        m['c'][c_index],
        m['neurongroups'][0][m['connections'][0][c_index][1]][2],
        m['neurongroups'][0][m['connections'][0][c_index][2]][2])
    return matrix
    
    
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
