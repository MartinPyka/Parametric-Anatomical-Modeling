import bpy
import sys

import pam
import pam_vis as pv
import config as cfg
import export

import code


EXPORT_PATH = '/home/martin/Dropbox/Work/Hippocampus3D/PAM/results/'


# get all important layers
dg = bpy.data.objects['DG_sg']
ca3 = bpy.data.objects['CA3_sp']
ca1 = bpy.data.objects['CA1_sp']
al_dg = bpy.data.objects['DG_sg_axons_all']
al_ca3 = bpy.data.objects['CA3_sp_axons_all']

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

pv.visualizeClean()
pam.initialize3D()

dg_params = [2., 0.5, 0., 0.]
ca3_params_dendrites = [0.2, 0.2, 0., 0.0]
ca3_params = [10., 0.5, -5., 0.00]


###################################################
## measure ration between real and UV-distances
###################################################
uv_data, layer_names = pam.measureUVs([al_dg, al_ca3])
export.export_UVfactors(EXPORT_PATH + 'UVscaling.zip', uv_data, layer_names)

3 / 0 
#namespace = globals().copy()
#namespace.update(locals())
#code.interact(local=namespace)

c_dg_ca3, d_dg_ca3, s_dg_ca3, grid = pam.computeConnectivity([dg, al_dg, ca3],                      # layers involved in the connection
                                           dg_neurons, ca3_neurons,       # neuronsets involved
                                           1,                                      # synaptic layer
                                           [cfg.MAP_euclid, cfg.MAP_euclid],                                 # connection mapping
                                           [cfg.DIS_euclid, cfg.DIS_euclid],                                 # distance calculation
                                           pam.connfunc_gauss_pre, dg_params, pam.connfunc_gauss_post, ca3_params_dendrites,   # kernel function plus parameters
                                           int(s_dg_ca3))                      # number of synapses for each  pre-synaptic neuron



if True:
    c_ca3_ca3, d_ca3_ca3, s_ca3_ca3, grid = pam.computeConnectivity([ca3, al_ca3, ca3],                      # layers involved in the connection
                                               'CA3_Pyramidal', 'CA3_Pyramidal',       # neuronsets involved
                                               1,                                      # synaptic layer
                                               [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
                                               [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
                                               pam.connfunc_gauss_pre, ca3_params, pam.connfunc_gauss_post, ca3_params_dendrites,   # kernel function plus parameters
                                               int(s_ca3_ca3 * f))                      # number of synapses for each  pre-synaptic neuron
                                               
print(pam.pam_connection_counter)
print(pam.pam_connections)
print(pam.pam_ng_list)

   
print("Visualization")    

particle = 21
    
#pv.visualizePostNeurons(ca3, ca3_neurons, c_dg_ca3[particle])
pv.visualizeConnectionsForNeuron([ca3, al_ca3, ca3],                      # layers involved in the connection
                       ca3_neurons, ca3_neurons,       # neuronsets involved
                       1,                                      # synaptic layer
                       [cfg.MAP_normal, cfg.MAP_normal],                                 # connection mapping
                       [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
                       particle, c_ca3_ca3[particle], s_ca3_ca3[particle])



particle = 21
pv.setCursor(dg.particle_systems[dg_neurons].particles[particle].location)

pv.visualizeConnectionsForNeuron([dg, al_dg, ca3],                      # layers involved in the connection
                       dg_neurons, ca3_neurons,       # neuronsets involved
                       1,                                      # synaptic layer
                       [cfg.MAP_euclid, cfg.MAP_euclid],                                 # connection mapping
                       [cfg.DIS_euclid, cfg.DIS_euclid],                                 # distance calculation
                       particle, c_dg_ca3[particle], s_dg_ca3[particle])

print(c_dg_ca3[particle])

export.export_zip(EXPORT_PATH + 'hippocampus.zip', [c_dg_ca3, c_ca3_ca3], [d_dg_ca3, d_ca3_ca3], pam.pam_ng_list, pam.pam_connections)