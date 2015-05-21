import unittest
import pam
import bpy
import numpy
import mathutils

CONNECTIONS = [([bpy.data.objects['Pre'], bpy.data.objects['Synapse'], bpy.data.objects['Post']],
    'pam.neuron_group', 'pam.neuron_group', 1, [0, 0], [0, 0], 
    pam.mapping.kernel.gauss, [1.0, 1.0, 0.0, 0.0], 
    pam.mapping.kernel.gauss, [1.0, 1.0, 0.0, 0.0], 1)]

CONNECTION_RESULTS_LENGTH = 1
CONNECTION_RESULTS_LENGTH_C = 100
CONNECTION_INDICES = [[0, 1, 0]]

NG_DICT = {'Pre': {'pam.neuron_group': 1}, 'Post': {'pam.neuron_group': 0}}

NG_LIST = [['Post', 'pam.neuron_group', 100], ['Pre', 'pam.neuron_group', 100]]

class TestPamModelCreate(unittest.TestCase):
    def setUp(self):
        bpy.ops.pam.mapping_compute()

    def testConnections(self):
        """Test if correct objects, particle systems, kernel, etc. are saved in model.CONNECTIONS"""
        self.assertEqual(CONNECTIONS, pam.model.CONNECTIONS)

    def testConnectionResults(self):
        """Tests if the connection results have the correct length. 
        Can only test the length of elements because the results are random."""
        self.assertEqual(CONNECTION_RESULTS_LENGTH, len(pam.model.CONNECTION_RESULTS))
        self.assertEqual(CONNECTION_RESULTS_LENGTH_C, len(pam.model.CONNECTION_RESULTS[0]['c']))

    def testConnectionIndices(self):
        """Test if connection indices are correct"""
        self.assertEqual(CONNECTION_INDICES, pam.model.CONNECTION_INDICES)

    def testNeuronGroups(self):
        """Test if neuron groups have been correctly generated and if the connection between them is correct"""
        self.assertEqual(NG_LIST, pam.model.NG_LIST)
        self.assertEqual(NG_DICT, pam.model.NG_DICT)

if __name__ == '__main__':
    unittest.main(exit = False)