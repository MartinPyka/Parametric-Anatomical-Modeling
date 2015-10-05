""" This module captures all essential classes to model a layer.
A layer can be anything that either hosts neurons, synapses or their
projections coming from other layers."""

# import custom exceptions
# import generic code for uv23d and 3d2uv-mapping

class Abstract_Layer():
	""" Abstract class for implementing layers """
	
	def __init__(self):
		""" Abstract definition of constructor """
		pass

	def __str__(self):
		return type(self)
	
class Layer_2D(Abstract_Layer):
	""" Implements a layer as 2D-manifold """
	
	def __init__(self, obj_name):
		""" creates a 2d-manifold for the object with name obj_name """
		# check whether obj_name is an existing object and fullfills some
		# basic criteria
		self.obj_name = obj_name
	
	def from_3d_to_uv(self, vec_3d, uv_map_i):
		""" maps a given 3d-vector point on the mesh to its
		corresponding uv-coordinate for a given uv_map with
		index uv_map_i """
		# check if uv_map_i exist in obj, if not, raise Exception
		# call generic 3d2uv-function from utils-module
		pass
	
	def from_uv_to_3d(self, vec_2d, uv_map_i):
		""" maps a given uv-vector point on the mesh to its
		corresponding 3d-coordinate for a given uv_map with
		index uv_map_i """
		# check if uv_map_i exist in obj, if not, raise Exception
		# call generic 3d2uv-function from utils-module
		pass
	