import bpy
import sys

import pam
import model
import pam_vis
import export
import gauss_2d as kernel

import code
import profile

import imp

imp.reload(pam)
imp.reload(pam_vis)
imp.reload(model)
imp.reload(export)
imp.reload(kernel)


EXPORT_PATH = '/home/martin/Dropbox/Work/Hippocampus3D/PAM/results/'

def surface_area(obj):
    return sum([polygon.area for polygon in obj.data.polygons])

# get all important layers
dg = bpy.data.objects['DG_sg']
ca3 = bpy.data.objects['CA3_sp']
ca1 = bpy.data.objects['CA1_sp']
sub = bpy.data.objects['Subiculum']

al_dg = bpy.data.objects['DG_sg_axons_all']

al_ca3 = bpy.data.objects['CA3_sp_axons_all']

il_ca1 = bpy.data.objects['CA1_sp.002']
al_ca1 = bpy.data.objects['CA1_sp_axons_all']

ec2 = bpy.data.objects['EC_2']
ec2_1_i1 = bpy.data.objects['EC_2_axons.000']
ec2_1_i2 = bpy.data.objects['EC_2_axons.001']
ec2_1_i3 = bpy.data.objects['EC_2_axons.002']
ec2_1_i4 = bpy.data.objects['EC_2_axons.003']
ec2_1_i5 = bpy.data.objects['EC_2_axons.004']
ec2_1_i6 = bpy.data.objects['EC_2_axons.005']
ec2_1_synapses = bpy.data.objects['EC_2_axons.synapse_1']
ec2_ca3_synapse = bpy.data.objects['CA3_EC_synapses']

ec2_2_i1 = bpy.data.objects['EC_2_axons.010']
ec2_2_i2 = bpy.data.objects['EC_2_axons.020']
ec2_2_i3 = bpy.data.objects['EC_2_axons.030']
ec2_2_i4 = bpy.data.objects['EC_2_axons.040']
ec2_2_i5 = bpy.data.objects['EC_2_axons.050']
ec2_2_synapses = bpy.data.objects['EC_2_axons.synapse_2']

ec2_3_i1 = bpy.data.objects['EC_2_axons.100']
ec2_3_i2 = bpy.data.objects['EC_2_axons.200']
ec2_3_i3 = bpy.data.objects['EC_2_axons.300']
ec2_3_i4 = bpy.data.objects['EC_2_axons.400']
ec2_3_i5 = bpy.data.objects['EC_2_axons.500']
ec2_3_synapses = bpy.data.objects['EC_2_axons.synapse_3']

ca1_i1 = bpy.data.objects['CA1_sp.002']
ca1_i2 = bpy.data.objects['CA1_sp.003']
ca1_i3 = bpy.data.objects['CA1_sp.004']
ca1_synapses = bpy.data.objects['CA1_sp.005']

sub_i1 = bpy.data.objects['Subiculum.000']
sub_i2 = bpy.data.objects['Subiculum.001']
sub_i3 = bpy.data.objects['Subiculum.002']
sub_i4 = bpy.data.objects['Subiculum.003']
ec5 = bpy.data.objects['EC_5']

# get all important neuron groups
ec2_neurons = 'EC2_Pyramidal'
ec5_neurons = 'EC5_Pyramidal'
dg_neurons = 'Granule Cells'
ca3_neurons = 'CA3_Pyramidal'
ca1_neurons = 'CA1_Pyramidal'
sub_neurons = 'Sub_Pyramidal'

# number of neurons per layer
n_dg = 1200000
n_ca3 = 250000
n_ca1 = 390000
n_sub = int(n_ca1 * (surface_area(sub) / surface_area(ca1)))
n_ec = 110000

# number of outgoing connections
s_dg_ca3 = 15
s_ca3_ca3 = 60 # 6000
s_ca3_ca1 = 85 # 8580
s_ca1_sub = 15 
s_ec21_dg = 38 # 38400
s_sub_ec5 = int((n_ec * s_ec21_dg) / n_sub)
s_ca1_ec5 = int((n_ec * s_ec21_dg) / n_ca1)

f = 0.001     # factor for the neuron numbers

# adjust the number of neurons per layer
ec2.particle_systems[ec2_neurons].settings.count = int(n_ec * f)
ec5.particle_systems[ec5_neurons].settings.count = int(n_ec * f)
dg.particle_systems[dg_neurons].settings.count = int(n_dg * f)
ca3.particle_systems[ca3_neurons].settings.count = int(n_ca3 * f)
ca1.particle_systems[ca1_neurons].settings.count = int(n_ca1 * f)
sub.particle_systems[sub_neurons].settings.count = int(n_sub * f)

pam_vis.visualizeClean()
pam.initialize3D()

ec2_params = [5.0, 0.2, 0.0, 0.0]
dg_params = [2., 0.5, 0., 0.]
ca3_params = [10., 0.2, -7., 0.00]
ca1_params = [0.08, 0.08, 0.0, 0.0]
ca1_params_ec5 = [0.2, 0.2, 0.0, 0.0]
sub_params = [0.2, 0.2, 0.0, 0.0]

dg_params_dendrites = [0.2, 0.2, 0.0, 0.0]
ca3_params_dendrites = [0.2, 0.2, 0.0, 0.0]
ca1_params_dendrites = ca3_params_dendrites
sub_params_dendrites = [0.2, 0.2, 0.0, 0.0]
ec5_params_dendrites = [0.3, 0.3, 0.0, 0.0]

###################################################
## measure ratio between real and UV-distances
###################################################
uv_data, layer_names = pam.measureUVs([al_dg, al_ca3])
#exporter.export_UVfactors(EXPORT_PATH + 'UVscaling.zip', uv_data, layer_names)


if True:
    id_ec21_dg = pam.addConnection(
        [ec2, ec2_1_i1, ec2_1_i2, ec2_1_i3, ec2_1_i4, ec2_1_synapses, dg],
        ec2_neurons, dg_neurons,
        5,
        [pam.MAP_normal, pam.MAP_top, pam.MAP_normal, pam.MAP_top, pam.MAP_euclid, pam.MAP_normal],
        [pam.DIS_euclid, pam.DIS_euclid, pam.DIS_euclid, pam.DIS_jumpUV, pam.DIS_jumpUV, pam.DIS_normalUV],
        kernel.gauss,
        ec2_params,
        kernel.gauss,
        dg_params_dendrites,
        s_ec21_dg
        )

if True:
    id_ec22_dg = pam.addConnection(
        [ec2, ec2_2_i1, ec2_2_i2, ec2_2_i3, ec2_2_synapses, dg],
        ec2_neurons, dg_neurons,
        4,
        [pam.MAP_normal, pam.MAP_top, pam.MAP_top, pam.MAP_euclid, pam.MAP_normal],
        [pam.DIS_euclid, pam.DIS_euclid, pam.DIS_jumpUV, pam.DIS_jumpUV, pam.DIS_normalUV],
        kernel.gauss,
        ec2_params,
        kernel.gauss,
        dg_params_dendrites,
        s_ec21_dg
        )        

if True:
    id_ec23_dg = pam.addConnection(
        [ec2, ec2_3_i1, ec2_3_i2, ec2_3_i3, ec2_3_synapses, dg],
        ec2_neurons, dg_neurons,
        4,
        [pam.MAP_normal, pam.MAP_top, pam.MAP_top, pam.MAP_euclid, pam.MAP_normal],
        [pam.DIS_euclid, pam.DIS_euclid, pam.DIS_jumpUV, pam.DIS_jumpUV, pam.DIS_normalUV],
        kernel.gauss,
        ec2_params,
        kernel.gauss,
        dg_params_dendrites,
        s_ec21_dg
        )
        
#if True:
#    id_sub_ec5 = pam.addConnection(
#        [sub, sub_i1, sub_i2, sub_i3, ec5],
#        sub_neurons, ec5_neurons,
#        3,
#        [pam.MAP_normal, pam.MAP_top, pam.MAP_top, pam.MAP_euclid],
#        [pam.DIS_euclid, pam.DIS_UVnormal, pam.DIS_normalUV, pam.MAP_euclid],
#        kernel.gauss,
#        sub_params,
#        kernel.gauss,
#        ec5_params_dendrites,
#        s_sub_ec5
#        )

if True:
    id_dg_ca3 = pam.addConnection([dg, al_dg, ca3],                      # layers involved in the connection
       dg_neurons, ca3_neurons,       # neuronsets involved
       1,                                      # synaptic layer
       [pam.MAP_euclid, pam.MAP_euclid],                                 # connection mapping
       [pam.DIS_euclidUV, pam.DIS_euclid],                                 # distance calculation
       kernel.gauss,
       dg_params, 
       kernel.gauss, 
       ca3_params_dendrites,   # kernel function plus parameters
       int(s_dg_ca3))                      # number of synapses for each  pre-synaptic neuron

if True:
    id_ca3_ca3 = pam.addConnection([ca3, al_ca3, ca3],                      # layers involved in the connection
       ca3_neurons, ca3_neurons,       # neuronsets involved
       1,                                      # synaptic layer
       [pam.MAP_normal, pam.MAP_normal],                                 # connection mapping
       [pam.DIS_normalUV, pam.DIS_normalUV],                                 # distance calculation
       kernel.gauss,
       ca3_params, 
       kernel.gauss,
       ca3_params_dendrites,   # kernel function plus parameters
       int(s_ca3_ca3))                      # number of synapses for each  pre-synaptic neuron

if True:
    id_ca3_ca1 = pam.addConnection(
        [ca3, al_ca3, ca1],
        ca3_neurons,
        ca1_neurons,
        1,
        [pam.MAP_normal, pam.MAP_normal],
        [pam.DIS_normalUV, pam.DIS_euclid],
        kernel.gauss,
        ca3_params,
        kernel.gauss,
        ca1_params_dendrites,
        int(s_ca3_ca1)
        )

if True:
    id_ca1_sub = pam.addConnection(
        [ca1, ca1_i1, al_ca1, sub],
        ca1_neurons, sub_neurons,
        2,
        [pam.MAP_top, pam.MAP_top, pam.MAP_normal],
        [pam.DIS_euclid, pam.DIS_euclid, pam.DIS_euclidUV],
        kernel.gauss,
        ca1_params,
        kernel.gauss,
        sub_params_dendrites,
        s_ca1_sub
        )
        
if True:
    id_ca1_ec5 = pam.addConnection(
        [ca1, ca1_i1, ca1_i2, ca1_i3, ca1_synapses, ec5],
        ca1_neurons, ec5_neurons,
        4,
        [pam.MAP_normal, pam.MAP_top, pam.MAP_top, pam.MAP_top, pam.MAP_normal],
        [pam.DIS_euclid, pam.DIS_UVnormal, pam.DIS_euclid, pam.DIS_normalUV, pam.DIS_jumpUV],
        kernel.gauss,
        ca1_params_ec5,
        kernel.gauss,
        ec5_params_dendrites,
        s_ca1_ec5
        )

if True:
    id_sub_ec5 = pam.addConnection(
        [sub, sub_i1, sub_i2, sub_i3, sub_i4, ec5],
        sub_neurons, ec5_neurons,
        4,
        [pam.MAP_normal, pam.MAP_top, pam.MAP_top, pam.MAP_top, pam.MAP_normal],
        [pam.DIS_euclid, pam.DIS_UVnormal, pam.DIS_euclid, pam.DIS_normalUV, pam.DIS_jumpUV],
        kernel.gauss,
        sub_params,
        kernel.gauss,
        ec5_params_dendrites,
        s_sub_ec5
        )        

    
#    pam.addConnection(
#        layers=[ca3, al_ca3, ca1],
#        neuronset1=ca3_neurons,
#        neuronset2=ca1_neurons,
#        slayer=1,
#        connections=[config.MAP_normal, config.MAP_normal],
#        distances=[config.DIS_normalUV, config.DIS_euclid],
#        func_pre=pam.connfunc_gauss_pre,
#        args_pre=ca3_params,
#        func_post=kernel.gauss,
#        args_post=ca1_params_dendrites,
#        no_synapses=int(s_ca3_ca1 * 0.01)
#        )

pam.computeAllConnections()
#profile.run("pam.computeAllConnections()")
pam.printConnections()
                                               
#print(pam.pam_connection_counter)
#print(pam.pam_connections)
#print(pam.pam_ng_list)

   
print("Visualization")    

particle = 22

#p, n, f = ca3.closest_point_on_mesh(ca3.particle_systems[ca3_neurons].particles[particle].location)
#pam_vis.visualizePoint(pam.map3dPointTo3d(
#    al_ca3, al_ca3, p, n))

#namespace = globals().copy()
#namespace.update(locals())
#code.interact(local=namespace)
    

export.export_connections(EXPORT_PATH + 'hippocampus_full.zip')

for j in range(0, model.CONNECTION_COUNTER):
    print(j)
    for i in range(0,2):
        print(i)
        pam_vis.visualizeConnectionsForNeuron(j, i)
