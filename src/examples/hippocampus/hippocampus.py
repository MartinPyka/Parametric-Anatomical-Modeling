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


   
def analyseUVdata():
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
    mp.show()
    
def analyseNetwork():
    m = pam2nest.import_connections(EXPORT_PATH + 'hippocampus.zip')
    
    #nest_vis.plotDelayHistograms(m)
    nest_vis.printNeuronGroups(m)
    nest_vis.printConnections(m)

    #matrix = nest_vis.getConnectionMatrix(m, 2)
    #mp.figure()
    #mp.imshow(matrix)
    
        
    #mp.show()
    weights = [5.0, 2.5, 12.0, 10.0]
    ngs = pam2nest.CreateNetwork(m, 'izhikevich', weights, DELAY_FACTOR)
    
    # conn = FindConnections([ngs[3][0]])
    
    
    noise         = Create("poisson_generator", 1)
    voltmeter     = Create("voltmeter", 2)
    espikes       = Create("spike_detector")
    
    SetStatus(noise, [{"rate": 800.0}])

    DivergentConnect(noise, ngs[2], weight=[2.], delay=[1.])
#    Connect([voltmeter[0]], [g1[0]])
#    Connect([voltmeter[1]], [g2[int(m['c'][0][0][0])]])
#  
    ConvergentConnect(ngs[0] + ngs[1] + ngs[2] + ngs[4],espikes)
#
    Simulate(1000.0)
#    
##    nest.voltage_trace.from_device([voltmeter[0]])
##    nest.voltage_trace.from_device([voltmeter[1]])
##    nest.voltage_trace.show()  
#    
    nest.raster_plot.from_device(espikes, hist=True)
    nest.raster_plot.show()    

    
    
if __name__ == "__main__":

    #analyseUVdata()
    analyseNetwork()
    
    
    