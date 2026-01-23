# https://github.com/ntoll/Adafruit_CircuitPython_Radio/blob/master/tests/conftest.py
# this is necessary when running tests on one's personal machine and not the actual board

"""
This file ensures everything is in place to run PyTest based unit tests against
the adafruit_radio module. It works by using Python's mock library to add
MagicMock objects to sys.modules for the modules which are not available to
standard Python because they're CircuitPython only modules.

Such mocking happens as soon as this conftest.py file is imported (so the
mocked modules exist in sys.modules before the module to be tested is
imported), and immediately before each test function is evaluated (so changes
to state remain isolated between tests).
"""
import sys
from unittest.mock import MagicMock

sys.modules['micropython'] = MagicMock()


def get_unavailable_firmware_modules():
    import importlib
    import os
    import json

    res = []
    config_loc = os.getenv("RAPID-0-Software_test-config")
    firmware_modules = json.load(
        open(os.path.join(config_loc, "firmware_modules.json"))
    )
    for module in firmware_modules["STABLE"] + firmware_modules["PRERELEASE"]:
        if module not in sys.modules and importlib.util.find_spec(module) is None:
            res.append(module)
    return res


def mock_modules(MOCK_MODULES):
    """
    Mocks away the modules named in MOCK_MODULES, so the module under test
    can be imported with modules which may not be available.
    """
    module_paths = set()
    for m in MOCK_MODULES:
        namespaces = m.split(".")
        ns = []
        for n in namespaces:
            ns.append(n)
            module_paths.add(".".join(ns))
    for m_path in module_paths:
        sys.modules[m_path] = MagicMock()


def pytest_runtest_setup(item):
    """
    Called immediately before any test function is called.

    Recreates afresh the mocked away modules so state between tests remains
    isolated.
    """
    if sys.implementation.name != "circuitpython":
        MOCK_MODULES = get_unavailable_firmware_modules()
        mock_modules(MOCK_MODULES)
        # CircuitPython does something equivalent to this internally
        sys.path.append("lib")


# Initial pre-setup configuration needed to stop ImportError when importing modules
pytest_runtest_setup(None)
