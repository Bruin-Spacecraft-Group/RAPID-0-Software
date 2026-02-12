import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'drivers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'lib'))

import mmc5983ma

class MMC5983MA_Test(unittest.TestCase):
    
    def test_read_gauss_conversion(self):
        sensor = mmc5983ma.MMC5983MA(sck_pin=MagicMock(), mosi_pin=MagicMock(), miso_pin=MagicMock(), ss_pin=MagicMock())
        
        sensor.read_register = MagicMock()
        # null field case (0x80, 0x00 for each axis)
        def mock_read(buf, length=1):
            buf[0] = 0x80; buf[1] = 0x00  # X = 32768
            buf[2] = 0x80; buf[3] = 0x00  # Y = 32768
            buf[4] = 0x80; buf[5] = 0x00  # Z = 32768
        sensor.read_register = mock_read
        
        x, y, z = sensor.read_gauss()
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(z, 0.0)
        
if __name__ == "__main__":
    unittest.main()