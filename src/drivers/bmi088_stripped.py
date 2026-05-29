"""
Stripped implementation of the bmi088 SPI driver

Not async friendly implementation
"""

import digitalio
import busio

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

        self.cs.value = False # set low, opens/selects gyro
        dummy = bytearray(2)
        result = bytearray(1)
        self.spi.write_readinto(bytes([reg | 0x80]), dummy) # read bit -> 1
        self.spi.readinto(result)
        self.cs.value = True # deselect
        return dummy, result

    def test_chip_id(self):
        # spi config
        while not self.spi.try_lock():
            pass
        self.spi.configure(baudrate=1_000_000, phase=0, polarity=0)

        value = self._read_gyro_register(0x0F) # 0x0F is the chip id register
        self.spi.unlock()

        return value
