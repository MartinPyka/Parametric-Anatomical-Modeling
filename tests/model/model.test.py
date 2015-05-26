import unittest
import pam
import bpy
import numpy
import random
import pickle

SEED = 42

class TestAddon(unittest.TestCase):
    def testAddonEnabled(self):
        self.assertNotNone(pam.bl_info)

class TestPamModelCreate(unittest.TestCase):
    def setUp(self):
        # Seed the rng
        random.seed(SEED)

    def loadModel(self, path):
        snapshot = pickle.load(open(bpy.path.abspath(path), "rb"))
        self.NG_LIST = snapshot.NG_LIST
        self.NG_DICT = snapshot.NG_DICT
        self.CONNECTION_COUNTER = snapshot.CONNECTION_COUNTER
        self.CONNECTION_INDICES = snapshot.CONNECTION_INDICES
        self.CONNECTIONS = pam.model.Pickle2Connection(snapshot.CONNECTIONS)
        self.CONNECTION_RESULTS = pam.model.convertArray2Vector(snapshot.CONNECTION_RESULTS)

    def testModels(self):
        """Test if the pam model generated using euclidean mapping method is the same as a predefined model.

        Checks CONNECTIONS, CONNECTION_RESULTS, CONNECTION_INDICES, NG_LIST and NG_DICT"""
        # Import should-be pam model
        self.loadModel("//model.test.pam")

        # Compute mapping
        bpy.ops.pam.mapping_compute()

        for i in range(len(self.CONNECTIONS)):
            with self.subTest(i = i):
                self.assertEqual(self.CONNECTIONS[i], pam.model.CONNECTIONS[i], "Connections between neuron groups differ")
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['c'], pam.model.CONNECTION_RESULTS[i]['c'], "Connections are not equal in connection ID " + str(i))
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['d'], pam.model.CONNECTION_RESULTS[i]['d'], "Distances between connections are incorrect in connection ID " + str(i))
                self.assertEqual(self.CONNECTION_RESULTS[i]['s'], pam.model.CONNECTION_RESULTS[i]['s'], "Synapse vectors are incorrect for connection " + str(i))
                self.assertEqual(self.CONNECTION_INDICES[i], pam.model.CONNECTION_INDICES[i], "Connection indices are incorrect")
                self.assertEqual(self.NG_LIST[i], pam.model.NG_LIST[i], "Neuron group list is incorrect")
            self.assertEqual(self.NG_DICT, pam.model.NG_DICT, "Neuron group dictionary is incorrect")

def run():
    """Run unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPamModelCreate))
    unittest.TextTestRunner(verbosity=2).run(suite)

bpy.ops.wm.addon_enable(module='pam')
run()