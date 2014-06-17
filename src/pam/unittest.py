import bpy
from pam import pam
from pam import pam_vis
from pam.kernel import gauss_2d as kernel
from pam import model
import random
import numpy

import pickle

EXPORT_PATH = '/home/martin/ownCloud/work/Projekte/hippocampal_model/results/'

p1 = bpy.data.objects['Plane']
p2 = bpy.data.objects['Plane.001']
p3 = bpy.data.objects['Plane.002']

pam_vis.visualizeClean()
pam.initialize3D()

random.seed(1)


id1 = pam.addConnection(
    [p1, p2, p3],
    'ParticleSystem', 'ParticleSystem',
    1,
    [pam.MAP_top, pam.MAP_top],
    [pam.DIS_jumpUV, pam.DIS_euclid],
    kernel.gauss,
    [0.2, 0.2, 0., 0.],
    kernel.gauss,
    [0.2, 0.2, 0., 0.],
    1
    )
pam.computeAllConnections()
path = pam_vis.visualizeConnectionsForNeuron(id1, 8)

create_reference = False


if create_reference:
    reference = model.save(EXPORT_PATH + 'test_universal.pam')
    
    f = open(EXPORT_PATH + 'test_universal.path', 'wb')
    pickle.dump(numpy.array(path), f)
    f.close()
    

reference = model.load(EXPORT_PATH + 'test_universal.pam')
result = model.ModelSnapshot()

print('Connections: ', str(reference.CONNECTION_RESULTS) == str(result.CONNECTION_RESULTS) )

f = open(EXPORT_PATH + 'test_universal.path', 'rb')
reference_path = pickle.load(f)
f.close()

print('Path: ', (path == reference_path).all())