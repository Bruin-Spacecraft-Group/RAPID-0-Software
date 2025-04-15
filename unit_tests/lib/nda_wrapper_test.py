import unittest
import sys

import nda_wrapper


class NDALib_Test(unittest.TestCase):
    def test_availability_check(self):
        self.assertIn(nda_wrapper.nda_libraries_available(), [True, False])

    def test_safe_import(self):
        self.assertIn(
            type(nda_wrapper.safe_import_nda_libraries()),
            [type(unittest), type(None)],
        )

    def conditional_execution_code(nda_libraries):
        nda_libraries.example.secret_function()

    def test_conditional_execution(self):
        nda_wrapper.run_if_nda_libraries_available(
            NDALib_Test.conditional_execution_code
        )
