# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 15:32:35 2014

@author: martin
"""

import importer as imp
import pam2nest as pn
import nest

# TODO (MP): merge importer and pam2nest

EXPORT_PATH = '/home/martin/Dropbox/Work/Hippocampus3D/PAM/models/'
DELAY_FACTOR = 4.0

if __name__ == "__main__":
    m = imp.import_zip(EXPORT_PATH + 'hippocampus.zip')
    
    g1 = nest.Create('iaf_neuron', len(m['c'][0]))
    g2 = nest.Create('iaf_neuron', 250)
    
    pn.Connect(g1, g2, m['c'][0], m['d'][0], 2.0, DELAY_FACTOR)
    conn = nest.FindConnections([g1[1]])
    print(nest.GetStatus(conn))
    