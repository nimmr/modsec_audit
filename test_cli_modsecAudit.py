import unittest
import test_modsecAudit
suite = unittest.TestLoader().loadTestsFromModule(test_modsecAudit)
unittest.TextTestRunner(verbosity=3).run(suite)

__author__ = 'Tim Lund <code@nimmr.dk>'
