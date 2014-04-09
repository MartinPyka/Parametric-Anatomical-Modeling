# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 15:32:35 2014

@author: martin
"""

import pam2nest
import matplotlib.pyplot as mp

from nest import *
import nest.voltage_trace
import nest.raster_plot
import numpy as np

import nest_vis

# TODO (MP): merge importer and pam2nest

EXPORT_PATH = '/home/martin/Dropbox/Work/Hippocampus3D/PAM/results/'
DELAY_FACTOR = 4.0


def plotDelayHistograms(m):
    
    for d in m['d']:
        mp.figure()
        c = np.array(d)
        c = c.flatten()
        print(c.var())
        mp.hist(c[c>0], 20)
    
    mp.title('connection histogram')
    
    
if __name__ == "__main__":

    data, names = pam2nest.import_UVfactors(EXPORT_PATH + "UVscaling.zip")    
    x_data = []
    y_data = []

    print(names)
    for i, d in enumerate(data):
        x_data = np.concatenate((x_data, np.ones(len(d[0]))*(i+1)))
        y_data = y_data + d[0]
        
    mp.figure()
    mp.plot(x_data, y_data, '*')
    
#    mp.figure()
#    mp.hist(data[0][0])
#    mp.figure()
#    mp.hist(data[1][0])
    
    print('var: ', np.var(data[0][0]))
    print('var: ', np.var(data[1][0]))
    
    
    m = pam2nest.import_connections(EXPORT_PATH + 'hippocampus.zip')
    
    plotDelayHistograms(m)
    
    for i, c in enumerate(m['c']):
        print(m['neurongroups'][0][m['connections'][0][i][1]][0] + ' - ' +
              m['neurongroups'][0][m['connections'][0][i][2]][0])
        matrix = nest_vis.connectivityMatrix(
            c, 
            m['neurongroups'][0][m['connections'][0][i][1]][2],
            m['neurongroups'][0][m['connections'][0][i][2]][2])
            
        # mp.figure()
        # mp.imshow(matrix)
    
        
    mp.show()
    # ngs = pn.CreateNetwork(m, 'iaf_neuron', 20.0, DELAY_FACTOR)
    
    # conn = FindConnections([ngs[3][0]])
    
    
#    noise         = Create("poisson_generator", 1)
#    voltmeter     = Create("voltmeter", 2)
#    espikes       = Create("spike_detector")
#    
#    SetStatus(noise, [{"rate": 800.0}])
#
#    DivergentConnect(noise, [g1[0]], weight=[100.], delay=[10.])
#    Connect([voltmeter[0]], [g1[0]])
#    Connect([voltmeter[1]], [g2[int(m['c'][0][0][0])]])
#  
#    ConvergentConnect(g1,espikes)
#
#    Simulate(500.0)
#    
##    nest.voltage_trace.from_device([voltmeter[0]])
##    nest.voltage_trace.from_device([voltmeter[1]])
##    nest.voltage_trace.show()  
#    
#    nest.raster_plot.from_device(espikes, hist=True)
#    nest.raster_plot.show()
    