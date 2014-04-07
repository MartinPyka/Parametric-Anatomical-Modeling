# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 15:32:35 2014

@author: martin
"""

import pam2nest as pn

from nest import *
import nest.voltage_trace
import nest.raster_plot

# TODO (MP): merge importer and pam2nest

EXPORT_PATH = '/home/martin/Dropbox/Work/Hippocampus3D/PAM/models/'
DELAY_FACTOR = 4.0

if __name__ == "__main__":
    m = pn.import_zip(EXPORT_PATH + 'hippocampus.zip')
    
    ngs = pn.CreateNetwork(m, 'iaf_neuron', 20.0, DELAY_FACTOR)
    
    conn = FindConnections([ngs[3][0]])
    
    
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
    