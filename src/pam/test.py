#filename = "/home/martin/ownCloud/work/Projekte/parametric-anatomical-modeling/src/pam/pam.py"
#exec(compile(open(filename).read(), filename, 'exec'))


import bpy
from mathutils import *
import pam_vis as pv
import config as cfg
import pam
import numpy as np
import pickle
        

# get all important layers
dg = bpy.data.objects['DG_sg']
ca3 = bpy.data.objects['CA3_sp']
ca1 = bpy.data.objects['CA1_sp']
al_dg = bpy.data.objects['DG_sg_axons_all']
al_ca3 = bpy.data.objects['CA3_sp_axons_all']
ca = bpy.data.objects['CA']

# get all important neuron groups
ca3_neurons = 'CA3_Pyramidal'
ca1_neurons = 'CA1_Pyramidal'

g, c1, d1, s1, c2, d2, s2 = pam.test()
rd1 = pam.computeDistance(ca3, ca3, ca3_neurons, ca3_neurons, ca, c1)
rd2 = pam.computeDistance(ca3, ca1, ca3_neurons, ca1_neurons, ca, c2)

a = np.where((rd1 < 1.0) & (d1 > 1.8))

print('Real distance: ', rd1[a[0][0], a[1][0]])
print('Connection distance: ', d1[a[0][0], a[1][0]])

pv.visualizeClean()

pv.setCursor(ca3.particle_systems[ca3_neurons].particles[a[0][0]].location)
pv.visualizePoint(ca3.particle_systems[ca3_neurons].particles[c1[a[0][0],a[1][0]]].location)
print(s1[a[0][0]][a[1][0]])
print(pam.mapUVPointTo3d(al_ca3, s1[a[0][0]][a[1][0]]))
pv.visualizePoint(pam.mapUVPointTo3d(al_ca3, s1[a[0][0]][a[1][0]]))

for i in range(0, len(a[0])):
    pv.visualizeOneConnection([ca3, al_ca3, ca3],                      # layers involved in the connection
                              ca3_neurons, ca3_neurons,       # neuronsets involved
                              1,                                      # synaptic layer
                              [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
                              [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
                              a[0][i],
                              c1[a[0][i], a[1][i]], a[1][i], s1[a[0][i]])
                              
data = [d1.tolist(), rd1.tolist()]
f = open('/home/martin/data.bin', 'wb')
pickle.dump(data, f, protocol = 2)
f.close()
         
data = [d2.tolist(), rd2.tolist()]
f = open('/home/martin/data2.bin', 'wb')
pickle.dump(data, f, protocol = 2)
f.close()                          
                          
#a = np.where(d1[45] == np.max(d1[45]))
#i = a[0][0]
#
#print(np.max(d1[45]))
#print(np.max(d2[45]))
#print(i)
#
#pv.visualizeClean()
#pv.visualizeOneConnection([ca3, al_ca3, ca3],                      # layers involved in the connection
#                                 ca3_neurons, ca3_neurons,      # neuronsets involved
#                                 1,                                      # synaptic layer
#                                 [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
#                                 [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
#                                 particle,
#                                 c1[particle, i], i, s1[particle])
#
#p3d, p2d, d = pam.computeMapping([ca3, al_ca3], [cfg.MAP_normal], [cfg.DIS_normalUV], ca3.particle_systems[0].particles[45].location)                                          
#print(d)
#print("  ")
#print(s1[particle][i])
#
#p = pam.mapUVPointTo3d(al_ca3, s1[particle][i])
#print(p)
#if (p != None):
#    pv.visualizePoint(p)
#
#print("  ")
#         
#a = np.where(d2[45] == np.max(d2[45]))
#i = a[0][0]
#print(i)                
#
#pv.visualizeOneConnection([ca3, al_ca3, ca1],                      # layers involved in the connection
#                                 ca3_neurons, ca1_neurons,       # neuronsets involved
#                                 1,                                      # synaptic layer
#                                 [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
#                                 [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
#                                 particle,
#                                 c2[particle, i], i, s2[particle])   
#                                 
#print("  ")                                         
#print(s2[particle][i])
#
#p = pam.mapUVPointTo3d(al_ca3, s2[particle][i])
#print(p)
#if (p != None):
#    pv.visualizePoint(p)