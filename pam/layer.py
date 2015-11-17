import mesh

class AbstractLayer():
    """Abstract layer for implementing layers"""

    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name

class Layer2d(AbstractLayer):
    """Implements a layer as a 2D-manifold"""
    def __init__(self, name, obj):
        super().__init__(name)
        self.obj = obj

    def map3dPointToUV(self, point, normal = None):
        """Wrapper function for mesh.map3dPointToUV"""
        return mesh.map3dPointToUV(self.obj, self.obj, point, normal)

    def mapUVPointTo3d(self, uv_list):
        """Wrapper function for mesh.mapUVPointTo3d"""
        return mesh.mapUVPointTo3d(self.obj, self.obj, uv)

    def map3dPointTo3d(self, point, layer2d, normal = None):
        """Wrapper function for mesh.map3dPointTo3d"""
        return mesh.map3dPointTo3d(self.obj, layer2d.obj, point, normal)

    def interpolateUVTrackIn3d(uv_p1, uv_p2):
        return mesh.interpolateUVTrackIn3d(p1, p2, self.obj)

    def closest_point_on_mesh(self, point):
        """Wrapper function for bpy.types.object.closest_point_on_mesh"""
        return obj.closest_point_on_mesh(point)

    def raycast(self, origin, direction):
        """Wrapper function for bpy.types.object.raycast"""
        return obj.raycast(origin, direction)

class NeuronLayer(Layer2d):
    """Implements a 2d-layer with neurons on it"""

    def __init__(self, name, mesh, neurons, kernel):
        super().__init__(name, mesh)
        self.neurons = neurons
        self.kernel = kernel
        self.neuron_count = len(neurons)

    def getNeuronPosition(self, index):
        """Returns the 3d point of the neuron with the given index
        :param index: The index of the neuron
        :type index: int
        :return: The position of the neuron
        :rtype: mathutils.Vector"""
        return self.neurons[index].position

class SynapticLayer(Layer2d):
    """Implements a 2d-layer with a number of synapses on it"""

    def __init__(self, name, mesh, no_synapses):
        super().__init__(name, mesh)
        self.no_synapses = no_synapses
