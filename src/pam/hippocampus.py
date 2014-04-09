import bpy
import sys

import pam
import pam_vis
import config
import exporter

import code

import imp

imp.reload(pam)
imp.reload(pam_vis)
imp.reload(config)
imp.reload(exporter)

EXPORT_PATH = '/home/martin/Dropbox/Work/Hippocampus3D/PAM/results/'


# get all important layers
dg = bpy.data.objects['DG_sg']
ca3 = bpy.data.objects['CA3_sp']
ca1 = bpy.data.objects['CA1_sp']
al_dg = bpy.data.objects['DG_sg_axons_all']
al_ca3 = bpy.data.objects['CA3_sp_axons_all']

ec2 = bpy.data.objects['EC_2']
ec2_1_i1 = bpy.data.objects['EC_2_axons.000']
ec2_1_i2 = bpy.data.objects['EC_2_axons.001']
ec2_1_i3 = bpy.data.objects['EC_2_axons.002']
ec2_1_i3 = bpy.data.objects['EC_2_axons.003']
ec2_1_synapses = bpy.data.objects['EC_2_axons.synapse_1']

ec2_2_i1 = bpy.data.objects['EC_2_axons.010']

ec2_3_i1 = bpy.data.objects['EC_2_axons.100']


# get all important neuron groups
dg_neurons = 'Granule Cells'
ca3_neurons = 'CA3_Pyramidal'
ca1_neurons = 'CA1_Pyramidal'

# number of neurons per layer
n_dg = 1200000
n_ca3 = 250000
n_ca1 = 390000

# number of outgoing connections
s_ca3_ca3 = 60000
s_dg_ca3 = 50 # 15

f = 0.001     # factor for the neuron numbers

# adjust the number of neurons per layer
ca3.particle_systems[ca3_neurons].settings.count = int(n_ca3 * f)
dg.particle_systems[dg_neurons].settings.count = int(n_dg * f)

pam_vis.visualizeClean()
pam.initialize3D()

dg_params = [2., 0.5, 0., 0.]
ca3_params_dendrites = [0.3, 0.3, 0., 0.0]
ca3_params = [10., 0.3, -7., 0.00]


###################################################
## measure ratio between real and UV-distances
###################################################
#uv_data, layer_names = pam.measureUVs([al_dg, al_ca3])
#exporter.export_UVfactors(EXPORT_PATH + 'UVscaling.zip', uv_data, layer_names)

#3 / 0 


c_dg_ca3, d_dg_ca3, s_dg_ca3, grid = pam.computeConnectivity([dg, al_dg, ca3],                      # layers involved in the connection
                                           dg_neurons, ca3_neurons,       # neuronsets involved
                                           1,                                      # synaptic layer
                                           [config.MAP_euclid, config.MAP_euclid],                                 # connection mapping
                                           [config.DIS_euclidUV, config.DIS_euclid],                                 # distance calculation
                                           pam.connfunc_gauss_pre, dg_params, pam.connfunc_gauss_post, ca3_params_dendrites,   # kernel function plus parameters
                                           int(s_dg_ca3))                      # number of synapses for each  pre-synaptic neuron



if True:
    c_ca3_ca3, d_ca3_ca3, s_ca3_ca3, grid = pam.computeConnectivity([ca3, al_ca3, ca3],                      # layers involved in the connection
                                               'CA3_Pyramidal', 'CA3_Pyramidal',       # neuronsets involved
                                               1,                                      # synaptic layer
                                               [config.MAP_normal, config.MAP_normal],                                 # connection mapping
                                               [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
                                               pam.connfunc_gauss_pre, ca3_params, pam.connfunc_gauss_post, ca3_params_dendrites,   # kernel function plus parameters
                                               int(s_ca3_ca3 * f))                      # number of synapses for each  pre-synaptic neuron

                                               
                                               
                                               
#print(pam.pam_connection_counter)
#print(pam.pam_connections)
#print(pam.pam_ng_list)

   
print("Visualization")    

particle = 24

p, n, f = ca3.closest_point_on_mesh(ca3.particle_systems[ca3_neurons].particles[particle].location)
pam_vis.visualizePoint(pam.map3dPointTo3d(
    al_ca3, al_ca3, p, n))

#namespace = globals().copy()
#namespace.update(locals())
#code.interact(local=namespace)
    

pam_vis.setCursor(ca3.particle_systems[ca3_neurons].particles[particle].location)    
pam_vis.visualizePostNeurons(ca3, ca3_neurons, c_ca3_ca3[particle])
pam_vis.visualizeConnectionsForNeuron([ca3, al_ca3, ca3],                      # layers involved in the connection
                       ca3_neurons, ca3_neurons,       # neuronsets involved
                       1,                                      # synaptic layer
                       [config.MAP_normal, config.MAP_normal],                                 # connection mapping
                       [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
                       particle, c_ca3_ca3[particle], s_ca3_ca3[particle])



particle = 22
#pam_vis.setCursor(dg.particle_systems[dg_neurons].particles[particle].location)

pam_vis.visualizePostNeurons(ca3, ca3_neurons, c_dg_ca3[particle])
pam_vis.visualizeConnectionsForNeuron([dg, al_dg, ca3],                      # layers involved in the connection
                       dg_neurons, ca3_neurons,       # neuronsets involved
                       1,                                      # synaptic layer
                       [config.MAP_euclid, config.MAP_euclid],                                 # connection mapping
                       [config.DIS_euclidUV, config.DIS_euclid],                                 # distance calculation
                       particle, c_dg_ca3[particle], s_dg_ca3[particle])

print(c_dg_ca3[particle])

exporter.export_connections(EXPORT_PATH + 'hippocampus.zip', [c_dg_ca3, c_ca3_ca3], [d_dg_ca3, d_ca3_ca3], pam.pam_ng_list, pam.pam_connections)