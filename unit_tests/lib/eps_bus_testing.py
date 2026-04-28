import unittest
import sys
import custom_module_mocking
from datastores import DsCommands
from unittest.mock import MagicMock

# 1. Mock the hardware-specific CircuitPython modules before import
sys.modules['board'] = MagicMock()

# Now it is safe to import your hardware-dependent module
import eps_bus_testing


class EpsBusTest(unittest.TestCase):

    def setUp(self):
        """Set up a fresh DummyDsCommands instance before each test."""
        self.ds_commands = DsCommands()

    def test_set_3v3(self):
        # Test enabling
        eps_bus_testing.set_3v3(self.ds_commands, True)
        self.assertTrue(eps_bus_testing.en_3v3_bus_pin.value)
        self.assertTrue(self.ds_commands.bus_3v3_enabled)

        # Test disabling
        eps_bus_testing.set_3v3(self.ds_commands, False)
        self.assertFalse(eps_bus_testing.en_3v3_bus_pin.value)
        self.assertFalse(self.ds_commands.bus_3v3_enabled)

    def test_set_5v(self):
        # Test enabling
        eps_bus_testing.set_5v(self.ds_commands, True)
        self.assertTrue(eps_bus_testing.en_5v_bus_pin.value)
        self.assertTrue(self.ds_commands.bus_5v_enabled)

        # Test disabling
        eps_bus_testing.set_5v(self.ds_commands, False)
        self.assertFalse(eps_bus_testing.en_5v_bus_pin.value)
        self.assertFalse(self.ds_commands.bus_5v_enabled)

    def test_set_12vlp(self):
        # Test enabling
        eps_bus_testing.set_12vlp(self.ds_commands, True)
        self.assertTrue(eps_bus_testing.en_12vlp_bus_pin.value)
        self.assertTrue(self.ds_commands.bus_12vlp_enabled)

        # Test disabling
        eps_bus_testing.set_12vlp(self.ds_commands, False)
        self.assertFalse(eps_bus_testing.en_12vlp_bus_pin.value)
        self.assertFalse(self.ds_commands.bus_12vlp_enabled)

    def test_set_12vhp(self):
        # Test enabling
        eps_bus_testing.set_12vhp(self.ds_commands, True)
        self.assertTrue(eps_bus_testing.en_12vhp_bus_pin.value)
        self.assertTrue(self.ds_commands.bus_12vhp_enabled)

        # Test disabling
        eps_bus_testing.set_12vhp(self.ds_commands, False)
        self.assertFalse(eps_bus_testing.en_12vhp_bus_pin.value)
        self.assertFalse(self.ds_commands.bus_12vhp_enabled)


if __name__ == "__main__":
    unittest.main()