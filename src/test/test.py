import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))

from test_model import TestModelComparison

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestModelComparison))
    unittest.TextTestRunner(verbosity=1).run(suite)
