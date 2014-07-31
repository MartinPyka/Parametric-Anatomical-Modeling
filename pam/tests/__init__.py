"""Testsuite module"""

import unittest

from .test_model import TestModelComparison


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestModelComparison))
    unittest.TextTestRunner(verbosity=2).run(suite)
