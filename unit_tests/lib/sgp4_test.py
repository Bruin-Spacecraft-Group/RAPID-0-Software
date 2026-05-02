import unittest
import math
from tle import Satrec

try:
    import ulab.numpy as np  # For CircuitPython
except ImportError:
    import numpy as np  # For GitHub Actions / PC testing

class PropagatorTest(unittest.TestCase):
    pass
