"""Testsuite module"""

import unittest

from .test_example import TestExample


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestExample))
    unittest.TextTestRunner(verbosity=2).run(suite)
