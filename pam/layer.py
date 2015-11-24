from . import mesh

class AbstractLayer():
    """Abstract layer for implementing layers"""

    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name

class Layer2d(AbstractLayer):
    """Implements a layer as a 2D-manifold"""
    def __init__(self, name, obj, uv_scaling = (1.0, 1.0)):
        super().__init__(name)
        self.obj = obj
        self.uv_scaling = uv_scaling

    def map3dPointToUV(self, point, normal = None):
        """Wrapper function for mesh.map3dPointToUV"""
        return mesh.map3dPointToUV(self.obj, self.obj, point, normal)

    def mapUVPointTo3d(self, uv_list):
        """Wrapper function for mesh.mapUVPointTo3d"""
        return mesh.mapUVPointTo3d(self.obj, uv_list)

    def map3dPointTo3d(self, layer2d, point, normal = None):
        """Wrapper function for mesh.map3dPointTo3d"""
        return mesh.map3dPointTo3d(self.obj, layer2d.obj, point, normal)

    def interpolateUVTrackIn3D(self, uv_p1, uv_p2):
        return mesh.interpolateUVTrackIn3D(uv_p1, uv_p2, self.obj)

    def closest_point_on_mesh(self, point):
        """Wrapper function for bpy.types.object.closest_point_on_mesh"""
        return self.obj.closest_point_on_mesh(point)

    def raycast(self, origin, direction):
        """Wrapper function for bpy.types.object.raycast"""
        return self.obj.raycast(origin, direction)

class NeuronLayer(Layer2d):
    """Implements a 2d-layer with neurons on it"""

    def __init__(self, name, obj, neuronset_name, neuronset, kernel):
        super().__init__(name, obj)
        self.neuronset = neuronset
        self.neuronset_name = neuronset_name
        self.kernel = kernel
        self.neuron_count = len(neuronset)

    def getNeuronPosition(self, index):
        """Returns the 3d point of the neuron with the given index
        :param index: The index of the neuron
        :type index: int
        :return: The position of the neuron
        :rtype: mathutils.Vector"""
        return self.neuronset[index].location

class SynapticLayer(Layer2d):
    """Implements a 2d-layer with a number of synapses on it"""

    def __init__(self, name, obj, no_synapses):
        super().__init__(name, obj)
        self.no_synapses = no_synapses
