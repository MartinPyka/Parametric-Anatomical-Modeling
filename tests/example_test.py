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


class TestExample(unittest.TestCase):
    """Example Testcase"""
    def setUp(self):
        """Setup test environment"""
        logging.disable(logging.CRITICAL)

    def test_one(self):
        """Example test one"""
        pass

    def test_two(self):
        """Example test two"""
        pass

    def tearDown(self):
        """Tear down test environment"""
        pass


def run():
    """Run unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestExample))
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run()
