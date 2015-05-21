import unittest
import pam
import bpy
import numpy
import random
import pickle

SEED = 42

class TestPamModelCreate(unittest.TestCase):
    def setUp(self):
        # Import should-be pam model
        snapshot = pickle.load(open(bpy.path.abspath("//model_test.pam"), "rb"))

        self.NG_LIST = snapshot.NG_LIST
        self.NG_DICT = snapshot.NG_DICT
        self.CONNECTION_COUNTER = snapshot.CONNECTION_COUNTER
        self.CONNECTION_INDICES = snapshot.CONNECTION_INDICES
        self.CONNECTIONS = pam.model.Pickle2Connection(snapshot.CONNECTIONS)
        self.CONNECTION_RESULTS = pam.model.convertArray2Vector(snapshot.CONNECTION_RESULTS)

        # Seed the rng
        random.seed(SEED)

        # Compute mapping
        bpy.ops.pam.mapping_compute()

    def testModel(self):
        """Test if the pam model generated is the same as a predefined model.

        Checks CONNECTIONS, CONNECTION_RESULTS, CONNECTION_INDICES, NG_LIST and NG_DICT"""
        
        self.assertEqual(self.CONNECTIONS, pam.model.CONNECTIONS, "Connections between neuron groups differ")
        self.assertEqual(len(self.CONNECTION_RESULTS), len(pam.model.CONNECTION_RESULTS), "Connection results do not have the correct length")
        for i in range(len(self.CONNECTION_RESULTS)):
            with self.subTest(i=i):
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['c'], pam.model.CONNECTION_RESULTS[i]['c'], "Connections are not equal in connection ID " + str(i))
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['d'], pam.model.CONNECTION_RESULTS[i]['d'], "Distances between connections are incorrect in connection ID " + str(i))
                self.assertEqual(self.CONNECTION_RESULTS[i]['s'], pam.model.CONNECTION_RESULTS[i]['s'], "Synapse vectors are incorrect for connection " + str(i))
        self.assertEqual(self.CONNECTION_INDICES, pam.model.CONNECTION_INDICES, "Connection indices are incorrect")
        self.assertEqual(self.NG_LIST, pam.model.NG_LIST, "Neuron group list is incorrect")
        self.assertEqual(self.NG_DICT, pam.model.NG_DICT, "Neuron group dictionary is incorrect")

if __name__ == '__main__':
    unittest.main(exit = False, verbosity = 2)