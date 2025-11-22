"""
Driver module for the MMC5983MA SPI 3-axis magnetometer from Memsic Inc.

"""

import pin_manager
import digitalio
import busio
from adafruit_bus_device.spi_device import SPIDevice


class MMC5983MA:
    def __init__(self, sck_pin, mosi_pin, miso_pin, ss_pin, _baudrate=1000000, _polarity = 0, _phase = 0):
        try:
            self.spi = busio.SPI(sck_pin, MOSI=mosi_pin, MISO=miso_pin)
        except ValueError as e:
            raise RuntimeError(
                "Failed to Initialize SPI. Check pin assignments."
            ) from e
        pm = pin_manager.PinManager.get_instance()
        self.baudrate = _baudrate
        self.polarity = _polarity
        self.phase = _phase
        self.ss_pin = pm.create_digital_in_out(ss_pin)
        self.ss_pin.direction = digitalio.Direction.OUTPUT
        self.ss_pin.value = True
        self.spi_device = SPIDevice(
            self.spi, self.ss_pin, baudrate=baudrate, polarity=0, phase=0
        )

    def read_register(self, register_address, length=1):
        with self.spi_device as spi:
            while not self.spi.try_lock():
                pass
            try:
                self.spi.configure(self.baudrate, self.polarity, self.phase)
                self.ss_pin.value = False
                self.spi.read(register_address)
                self.ss_pin.value = True
            finally:
                self.spi.unlock()


    def write_register(self, register_address):
        with self.spi as spi:
            while not self.spi.try_lock():
                pass
            try:
                self.spi.configure(self.baudrate, self.polarity, self.phase)
                self.ss_pin.value = False
                self.spi.write(register_address)
                self.ss_pin.value = True
            finally:
                self.spi.unlock()
