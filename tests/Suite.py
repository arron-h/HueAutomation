import unittest

import Method_SunSyncer_Test
import Method_Wakeup_Test

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(Method_SunSyncer_Test))
suite.addTests(loader.loadTestsFromModule(Method_Wakeup_Test))

runner = unittest.TextTestRunner()
reslt = runner.run(suite)
