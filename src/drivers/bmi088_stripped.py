"""
Stripped implementation of the bmi088 SPI driver

Not async friendly implementation
"""

import digitalio
import busio
import time

class Bmi088Gyroscope:
    """
    Only a driver for the gyroscope in the IMU
    """

    def __init__(self, spi: busio.SPI, cs_gyro):
        """

        """

        self.spi = spi
        self.cs = digitalio.DigitalInOut(cs_gyro)

        self.cs.direction = digitalio.Direction.OUTPUT
        self.cs.value = True # set pin high to deselect on initialisation

    def _read_gyro_register(self, reg: int):
        """
        Reads a singular register from the gyroscope on the device
        """
        while not self.spi.try_lock():
            print("fail")
            pass
        self.cs.value = False # set low, opens/selects gyro
        time.sleep(0.01)

        write = bytes([reg | 0x80, 0, 0,0,0,0,0,0,0,0])
        dummy = bytearray(10)
        self.spi.write_readinto(write, dummy) # read bit -> 1
        self.cs.value = True # deselect

        self.spi.unlock()
        return dummy

    def test_chip_id(self):
        # spi config
        value = self._read_gyro_register(0x00) # 0x00 is the chip id register
        return value
