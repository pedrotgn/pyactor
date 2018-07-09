"""
Local queries unittest module. General
@author: Daniel Barcelona Pons
"""
import unittest

from tests.unit.gevent import tests as gtests
from tests.unit.thread import tests

if __name__ == '__main__':
    print('## WITH THREADS')
    suite = unittest.TestLoader().loadTestsFromTestCase(tests.TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print('## WITH GREEN THREADS')
    suite = unittest.TestLoader().loadTestsFromTestCase(gtests.TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
