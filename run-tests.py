import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import unittest

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner().run(testsuite)
