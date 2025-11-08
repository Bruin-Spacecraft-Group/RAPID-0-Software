"""
Driver module for the MMC5983MA SPI 3-axis magnetometer from Memsic Inc.

"""

import pin_manager
import digitalio
import busio
from adafruit_bus_device.spi_device import SPIDevice


class MMC5983MA:
    def __init__(self, sck_pin, mosi_pin, miso_pin, ss_pin, baudrate=1000000):
        try:
            self.spi = busio.SPI(sck_pin, MOSI=mosi_pin, MISO=miso_pin)
        except ValueError as e:
            raise RuntimeError(
                "Failed to Initialize SPI. Check pin assignments."
            ) from e
        pm = pin_manager.PinManager.get_instance()
        self.ss_pin = pm.create_digital_in_out(ss_pin)
        self.ss_pin.direction = digitalio.Direction.OUTPUT
        self.ss_pin.value = True
        self.spi_device = SPIDevice(
            self.spi, self.ss_pin, baudrate=baudrate, polarity=0, phase=0
        )

    def read_register(self, register_address, length=1):
        with self.spi_device as spi:
            spi.write()
