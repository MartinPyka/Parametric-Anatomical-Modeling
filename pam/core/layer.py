"""Defines layer classes and layer connection classes"""

from mesh import *

class AbstractLayer():
    """Abstract layer for implementing layers"""

    def __init__(self, name, mesh):
        self.name = name
    
    def __str__(self):
        return self.name

class Layer2d(AbstractLayer):
    """Implements a layer as a 2D-manifold"""
    def __init__(self, name, mesh):
        super().__init__(name)
        self.mesh = mesh

    def map3dPointToUV(self, point, normal = None):
        self.mesh.map3dPointToUV(point, normal)

    def mapUVPointTo3d(self, uv):
        self.mesh.mapUVPointTo3d(uv)

    def closest_point_on_mesh(self, point):
        self.mesh.findClosestPointOnMesh(point)

class NeuronLayer(Layer2d):
    """Implements a 2d-layer with neurons on it"""

    def __init__(self, name, mesh, neurons, kernel):
        super().__init__(name, mesh)
        self.neurons = neurons
        self.kernel = kernel

class SynapticLayer(Layer2d):
    """Implements a 2d-layer with a number of synapses on it"""

    def __init__(self, name, mesh, no_synapses):
        super().__init__(name, mesh)
        self.no_synapses = no_synapses

class LayerConnection():
    """Implements an abstract connection between two layers"""
    mappingFunctionName = "AbstractMappingFunction"
    distanceFunctionName = "AbstractDistanceFunction"

    def __init__(self, pre_layer, post_layer):
        self.pre_layer = pre_layer
        self.post_layer = post_layer

    def __str__(self):
        return self.pre_layer.name + "->" + self.post_layer.name + ", Mapping: " + mappingFunctionName + ", Distance: " + distanceFunctionName

    def map(layerFrom, layerTo, p3d):
        return []

class LayerConnectionEuklidBase(LayerConnection):
    def map(layerFrom, layerTo, p3d):
        p3d_n = map3dPointTo3d(layerTo, layerTo, p3d)
        return [p3d_n]

class LayerConnectionNormalBase(LayerConnection):
    def map(layerFrom, layerTo, p3d):
        # compute normal on layer for the last point
        p, n, f = layerFrom.mesh.closest_point_on_mesh(p3d)
        # determine new point
        p3d_n = map3dPointTo3d(layerTo, layerTo, p, n)
        return p3d_n

layerConnectionTypes = {
    'euklid': {
        'euklid': (LayerConnectionEuklidBase, LayerConnection),
        'euklid_uv': (LayerConnectionEuklidBase, LayerConnectionEuklidBase),
        'jump_uv': (LayerConnectionEuklidBase, LayerConnectionEuklidBase),
        'uv_jump': None,
        'normal_uv': None,
        'uv_normal': None
    },
    'normal': {
        'euklid': None,
        'euklid_uv': None,
        'jump_uv': None,
        'uv_jump': None,
        'normal_uv': None,
        'uv_normal': None
    },
    'random': {
        'euklid': None,
        'euklid_uv': None,
        'jump_uv': None,
        'uv_jump': None,
        'normal_uv': None,
        'uv_normal': None
    },
    'topology': {
        'euklid': None,
        'euklid_uv': None,
        'jump_uv': None,
        'uv_jump': None,
        'normal_uv': None,
        'uv_normal': None
    },
    'uv': {
        'euklid': None,
        'euklid_uv': None,
        'jump_uv': None,
        'uv_jump': None,
        'normal_uv': None,
        'uv_normal': None
    }
    'mask3d' {
        'euklid': None,
        'euklid_uv': None,
        'jump_uv': None,
        'uv_jump': None,
        'normal_uv': None,
        'uv_normal': None
    }
}
