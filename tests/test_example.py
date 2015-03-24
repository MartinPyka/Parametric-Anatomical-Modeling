"""Testcase"""

import logging
import os
import unittest

import bpy

try:
    import pam
except ImportError:
    print("PAM not installed")
    sys.exit(1)

CURRENT_DIR = os.path.dirname(__file__)


class TestExample(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_one(self):
        """Example test one"""
        pass

    def test_two(self):
        """Example test two"""
        pass

    def tearDown(self):
        pass
