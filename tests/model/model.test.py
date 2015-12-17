import unittest
import pam
import bpy
import numpy
import random
import pickle
import sys

SEED = 42

class TestAddon(unittest.TestCase):
    def testAddonEnabled(self):
        self.assertNotNone(pam.bl_info)

class TestPamModelCreate(unittest.TestCase):
    def setUp(self):
        # Seed the rng
        random.seed(SEED)

    def loadModel(self, path):
        pam.model.loadZip(bpy.path.abspath(path))
        self.model = pam.model.MODEL
        self.CONNECTION_RESULTS = pam.model.CONNECTION_RESULTS
        pam.model.reset()
        
    def testModels(self):
        """Test if the pam model generated using euclidean mapping method is the same as a predefined model.

        Checks CONNECTIONS, CONNECTION_RESULTS, CONNECTION_INDICES, NG_LIST and NG_DICT"""
        # Import should-be pam model
        self.loadModel("//model.test.zip")

        # Compute mapping
        bpy.ops.pam.mapping_compute()

        for i in range(len(self.model.connections)):
            with self.subTest(i = i):
                self.assertEqual(self.model.connections[i], pam.model.MODEL.connections[i], "Connections between neuron groups differ")
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['c'], pam.model.CONNECTION_RESULTS[i]['c'], "Connections are not equal in connection ID " + str(i))
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['d'], pam.model.CONNECTION_RESULTS[i]['d'], "Distances between connections are incorrect in connection ID " + str(i))
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['s'], pam.model.CONNECTION_RESULTS[i]['s'], "Synapse vectors are incorrect for connection " + str(i))
                self.assertEqual(self.model.connection_indices[i], pam.model.MODEL.connection_indices[i], "Connection indices are incorrect")
                self.assertEqual(self.model.ng_list[i], pam.model.MODEL.ng_list[i], "Neuron group list is incorrect")
            self.assertEqual(self.model.ng_dict, pam.model.MODEL.ng_dict, "Neuron group dictionary is incorrect")

class TestPamModelThreaded(unittest.TestCase):
    def setUp(self):
        bpy.context.user_preferences.addons['pam'].preferences.use_threading = True
        bpy.context.user_preferences.addons['pam'].preferences.threads = 4

    def loadModel(self, path):
        pam.model.loadZip(bpy.path.abspath(path))
        self.model = pam.model.MODEL
        self.CONNECTION_RESULTS = pam.model.CONNECTION_RESULTS
        pam.model.reset()

    def testModels(self):
        """Test if the pam model generated using euclidean mapping method is the same as a predefined model when using multiple threads.
        Checks CONNECTIONS, CONNECTION_RESULTS, CONNECTION_INDICES, NG_LIST and NG_DICT"""
        # Import should-be pam model
        self.loadModel("//model.test.zip")

        # Compute mapping
        bpy.ops.pam.mapping_compute()

        for i in range(len(self.model.connections)):
            with self.subTest(i = i):
                self.assertEqual(self.model.connections[i], pam.model.MODEL.connections[i], "Connections between neuron groups differ")
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['c'], pam.model.CONNECTION_RESULTS[i]['c'], "Connections are not equal in connection ID " + str(i))
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['d'], pam.model.CONNECTION_RESULTS[i]['d'], "Distances between connections are incorrect in connection ID " + str(i))
                numpy.testing.assert_array_equal(self.CONNECTION_RESULTS[i]['s'], pam.model.CONNECTION_RESULTS[i]['s'], "Synapse vectors are incorrect for connection " + str(i))
                self.assertEqual(self.model.connection_indices[i], pam.model.MODEL.connection_indices[i], "Connection indices are incorrect")
                self.assertEqual(self.model.ng_list[i], pam.model.MODEL.ng_list[i], "Neuron group list is incorrect")
            self.assertEqual(self.model.ng_dict, pam.model.MODEL.ng_dict, "Neuron group dictionary is incorrect")

def run():
    """Run unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPamModelCreate))
    suite.addTest(unittest.makeSuite(TestPamModelThreaded))
    runner = unittest.TextTestRunner(verbosity=2)
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)

bpy.ops.wm.addon_enable(module='pam')
run()