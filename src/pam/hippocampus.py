import bpy

from pam import *
import pam_vis as pv
import config as cfg

# get all important layers
dg = bpy.data.objects['DG_sg']
ca3 = bpy.data.objects['CA3_sp']
ca1 = bpy.data.objects['CA1_sp']
al_dg = bpy.data.objects['DG_sg_axons_all']
al_ca3 = bpy.data.objects['CA3_sp_axons_all']

# get all important neuron groups
ca3_neurons = 'CA3_Pyramidal'
ca1_neurons = 'CA1_Pyramidal'

# number of neurons per layer
n_dg = 1200000
n_ca3 = 250000
n_ca1 = 390000

# number of outgoing connections
s_ca3_ca3 = 6000

f = 0.001     # factor for the neuron numbers

# adjust the number of neurons per layer
ca3.particle_systems[ca3_neurons].settings.count = int(n_ca3 * f)

pv.visualizeClean()
initialize3D()

ca3_params = [10., 1., -5., 0.00]

c_ca3_ca3, d_ca3_ca3, grid = computeConnectivity([ca3, al_ca3, ca3],                      # layers involved in the connection
                                           'CA3_Pyramidal', 'CA3_Pyramidal',       # neuronsets involved
                                           1,                                      # synaptic layer
                                           [cfg.MAP_top, cfg.MAP_euclid],                                 # connection mapping
                                           [cfg.DIS_normalUV, cfg.DIS_euclid],                                 # distance calculation
                                           connfunc_gauss_pre, ca3_params, connfunc_gauss_post, ca3_params,   # kernel function plus parameters
                                           int(s_ca3_ca3 * f))                      # number of synapses for each  pre-synaptic neuron
                                           
particle = 40
    
pv.setCursor(ca3.particle_systems[ca3_neurons].particles[particle].location)
    
pv.visualizePostNeurons(ca3, ca3_neurons, c_ca3_ca3[particle])                                           