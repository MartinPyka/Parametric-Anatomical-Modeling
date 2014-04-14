#filename = "/home/martin/ownCloud/work/Projekte/parametric-anatomical-modeling/src/pam/pam.py"
#exec(compile(open(filename).read(), filename, 'exec'))


import bpy
from mathutils import *
import pam_vis
import config
import pam
import numpy as np
import pickle
import helper

import imp

imp.reload(pam)
imp.reload(pam_vis)
imp.reload(config)
imp.reload(helper)

def connectiontest():
    pam.initialize3D()
    pam_vis.visualizeClean()

    t1 = bpy.data.objects['t1']
    t2 = bpy.data.objects['t2']
    t201 = bpy.data.objects['t2.001']
    t3 = bpy.data.objects['t3']
    t4 = bpy.data.objects['t4']
    t5 = bpy.data.objects['t5']

    params = [0.08, 0.08, 0.0, 0.0]

    c_id = pam.addConnection([t1, t2, t201, t3, t4, t5],                      # layers involved in the connection
                                           'ParticleSystem', 'ParticleSystem',       # neuronsets involved
                                           2,                                      # synaptic layer
                                           [config.MAP_top, config.MAP_top, config.MAP_top, config.MAP_top, config.MAP_top],
                                           [config.DIS_euclid, config.DIS_euclid, config.DIS_euclidUV, config.DIS_euclid, config.DIS_euclid],                                 # distance calculation
                                           pam.connfunc_gauss_pre, params, pam.connfunc_gauss_post, params,
                                           30)   # kernel function plus parameters

    # export.export_zip('test.zip', [conn], [dist])
    print(c_id)
    pam.computeAllConnections()

    pam_vis.visualizeConnectionsForNeuron(c_id, 3)
    pam_vis.visualizeConnectionsForNeuron(c_id, 4)
    pam_vis.visualizeConnectionsForNeuron(c_id, 5)
    pam_vis.visualizeConnectionsForNeuron(c_id, 6)


def gridTest():
    s = bpy.data.objects['CA3_sp_axons_all']
    g = helper.UVGrid(s)

    g.pre_kernel = pam.connfunc_gauss_post
    g.pre_kernel_args = [0.1, 0.1, 0.0, 0.0]
    g.post_kernel = pam.connfunc_gauss_post
    g.post_kernel_args = [0.1, 0.1, 0.0, 0.0]
    g.compute_preMask()
    g.compute_postMask()
    print(g._gridmask)
    
    

connectiontest()
#gridTest()       

## get all important layers
#dg = bpy.data.objects['DG_sg']
#ca3 = bpy.data.objects['CA3_sp']
#ca1 = bpy.data.objects['CA1_sp']
#al_dg = bpy.data.objects['DG_sg_axons_all']
#al_ca3 = bpy.data.objects['CA3_sp_axons_all']
#ca = bpy.data.objects['CA']
#
#
## get all important neuron groups
#ca3_neurons = 'CA3_Pyramidal'
#ca1_neurons = 'CA1_Pyramidal'
#
#g, c1, d1, s1, c2, d2, s2 = pam.test()
#rd1, p1, p2 = pam.computeDistance(ca3, ca3, ca3_neurons, ca3_neurons, ca, c1)
##rd2, _, _ = pam.computeDistance(ca3, ca1, ca3_neurons, ca1_neurons, ca, c2)
#
#a = np.where(d1 > 0)
#
#print(a[0][0])
#
##print('Real distance: ', rd1[a[0][0], a[1][0]])
##print('Connection distance: ', d1[a[0][0], a[1][0]])
##
##print('Distance: ', (p2[c1[a[0][0], a[1][0]]] - p1[a[0][0]]).length)
##
#pv.visualizeClean()
##
#pv.setCursor(ca3.particle_systems[ca3_neurons].particles[a[0][0]].location)
##pv.visualizePoint(ca3.particle_systems[ca3_neurons].particles[c1[a[0][0],a[1][0]]].location)
##print(s1[a[0][0]][a[1][0]])
###print(pam.mapUVPointTo3d(al_ca3, s1[a[0][0]][a[1][0]]))
##pv.visualizePoint(pam.mapUVPointTo3d(ca, p1[a[0][0]]))
##pv.visualizePoint(pam.mapUVPointTo3d(ca, p2[c1[a[0][0], a[1][0]]]))
###pv.visualizePoint(pam.mapUVPointTo3d(al_ca3, s1[a[0][0]][a[1][0]]))
##
#pv.visualizeConnectionsForNeuron([ca3, al_ca3, ca3],                      # layers involved in the connection
#                          ca3_neurons, ca3_neurons,       # neuronsets involved
#                          1,                                      # synaptic layer
#                          [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
#                          [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
#                          a[0][0],
#                          c1[a[0][0]], s1[a[0][0]])
#
#
##for i in range(0, len(a[0])):
##    pv.visualizeOneConnection([ca3, al_ca3, ca3],                      # layers involved in the connection
##                              ca3_neurons, ca3_neurons,       # neuronsets involved
##                              1,                                      # synaptic layer
##                              [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
##                              [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
##                              a[0][i],
##                              c1[a[0][i], a[1][i]], a[1][i], s1[a[0][i]])
#                              
##data = [d1.tolist(), rd1.tolist()]
##f = open('/home/martin/data.bin', 'wb')
##pickle.dump(data, f, protocol = 2)
##f.close()
##         
##data = [d2.tolist(), rd2.tolist()]
##f = open('/home/martin/data2.bin', 'wb')
##pickle.dump(data, f, protocol = 2)
##f.close()                          
#
##particle = 45
##                          
##a = np.where(rd1[particle] == np.max(rd1[particle]))
##i = a[0][0]
##
##print(rd1[particle][i])
##print(d1[particle][i])
##print(i)
##
##pv.visualizeClean()
##pv.visualizeOneConnection([ca3, al_ca3, ca3],                      # layers involved in the connection
##                                 ca3_neurons, ca3_neurons,      # neuronsets involved
##                                 1,                                      # synaptic layer
##                                 [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
##                                 [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
##                                 particle,
##                                 c1[particle, i], i, s1[particle])
##
##p3d, p2d, d = pam.computeMapping([ca3, al_ca3], [cfg.MAP_normal], [cfg.DIS_normalUV], ca3.particle_systems[0].particles[45].location)
##print(d)
##print("  ")
##print(s1[particle][i])
##
##p = pam.mapUVPointTo3d(al_ca3, s1[particle][i])
##print(p)
##if (p != None):
##    pv.visualizePoint(p)
##
##print("  ")
##         
##a = np.where(d2[45] == np.max(d2[45]))
##i = a[0][0]
##print(i)                
##
##pv.visualizeOneConnection([ca3, al_ca3, ca3],                      # layers involved in the connection
##                                 ca3_neurons, ca3_neurons,       # neuronsets involved
##                                 1,                                      # synaptic layer
##                                 [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
##                                 [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
##                                 particle,
##                                 c1[particle, i], i, s1[particle])   
##                                 
##print("  ")                                         
##print(s2[particle][i])
##
##p = pam.mapUVPointTo3d(al_ca3, s2[particle][i])
##print(p)
##if (p != None):
##    pv.visualizePoint(p)