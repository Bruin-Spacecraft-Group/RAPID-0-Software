"""
Driver module for the MMC5983MA SPI 3-axis magnetometer from Memsic Inc.

"""

import pin_manager
import digitalio


class MMC5983MA:
    def __init__(self, sck, mosi, miso, ss):
        pm = pin_manager.PinManager.get_instance()
        self.spi_bus = pm.create_spi(sck, mosi, miso)
        self.drdy_gpio = pm.create_digital_in_out(miso)
        self.ss_gpio = pm.create_digital_in_out(ss)
        with self.ss_gpio as ss_gpio:
            ss_gpio.direction = digitalio.Diretion.OUTPUT
            ss_gpio.value = True
