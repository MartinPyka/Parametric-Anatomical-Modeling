import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))

from test_model import TestModelComparison

suite = unittest.TestSuite()

suite.addTest(unittest.makeSuite(TestModelComparison))

unittest.TextTestRunner(verbosity=2).run(suite)
