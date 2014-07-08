import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir, "pam"))

from test_model import TestModelComparison

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestModelComparison))
    unittest.TextTestRunner(verbosity=1).run(suite)
