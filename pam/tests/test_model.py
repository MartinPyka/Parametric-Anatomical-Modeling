"""Testcase"""

import logging
import os
import pickle
import random
import unittest

import bpy
import numpy

from pam import model
from pam import pam
from pam import pam_vis
from pam.kernel import gaussian as kernel

CURRENT_DIR = os.path.dirname(__file__)


class TestModelComparison(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        random.seed(1)

        self.p1 = bpy.data.objects['Plane']
        self.p2 = bpy.data.objects['Plane.001']
        self.p3 = bpy.data.objects['Plane.002']
        self.p4 = bpy.data.objects['Plane.003']
        self.p5 = bpy.data.objects['Plane.004']
        self.p6 = bpy.data.objects['Plane.005']

        pam_vis.visualizeClean()
        pam.initialize3D()

        self.id1 = pam.addConnection(
            [self.p1, self.p2, self.p3],
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
        self.path = pam_vis.visualizeConnectionsForNeuron(self.id1, 8)

    def test_model_snapshot(self):
        """Docstrings will show up in the testrunner"""
        result = model.ModelSnapshot()
        reference = model.load(CURRENT_DIR + "/test_universal.pam")
        self.assertTrue(str(reference.CONNECTION_RESULTS) == str(result.CONNECTION_RESULTS))

    def test_model_path(self):
        """So you should use them"""
        with open(CURRENT_DIR + "/test_universal.path", "rb") as f:
            reference_path = pickle.load(f)
            self.assertTrue((self.path == reference_path).all())

    def tearDown(self):
        pass
