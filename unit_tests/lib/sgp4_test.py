import unittest
from tle import Satrec, jday

try:
    import ulab.numpy as np  # For CircuitPython
except ImportError:
    import numpy as np  # For GitHub Actions / PC testing


ISS_TLE = "ISS (ZARYA)\n1 25544U 98067A   26121.81277072  .00006771  00000-0  13067-3 0  9997\n2 25544  51.6311 169.6452 0007227  12.7206 347.3964 15.49051775564564"

class PropagatorTest(unittest.TestCase):
    
    def propagate_to_may_3(self):
        sat: Satrec = Satrec.from_tle_str(
            ISS_TLE
        )
    
        sgp4_obj = Satrec.sgp4_init(sat)
        error, r, v = sgp4_obj.sgp4_update(*jday(2026, 5, 3, 0, 0, 0))

        self.assertEqual(error, 0) # if no error,

        tol = 3 # to 3 decimal places
        self.assertAlmostEqual(r[0], 4698.782358, tol)
        self.assertAlmostEqual(r[1], -3867.014434, tol)
        self.assertAlmostEqual(r[2], 3028.549126, tol)

        tol = 6 # to 6 decimal places, these need to be more accurate
        self.assertAlmostEqual(v[0], 5.281325344, tol)
        self.assertAlmostEqual(v[1], 2.530170911, tol)
        self.assertAlmostEqual(v[2], -4.936649541, tol)
