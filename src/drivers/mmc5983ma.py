"""
Driver module for the MMC5983MA SPI 3-axis magnetometer from Memsic Inc.

"""

import pin_manager
import digitalio
import busio
#from adafruit_bus_device.spi_device import SPIDevice

"""
Register Addresses:

Magnetic output registers"
OUTX_L = 0x00 - X[17:10]
OUTX_H = 0x01 - X[9:2]
OUTY_L = 0x02
OUTY_H = 0x03
OUTZ_L = 0x04
OUTZ_H = 0x05

Other registers:
"""

COUNTS_PER_GAUSS_16BIT = 4096.0
NULL_FIELD_16BIT = 32768

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

# ---- SPI Interactions W/O SPIDevice ----
    # ---- Read and Write Interaction ----
    def read_and_write_register(self, read_register_address, write_register_address):
        while not self.spi.try_lock():
            pass
        try:
            self.spi.configure(self.baudrate, self.polarity, self.phase)
            self.ss_pin.value = False
            self.spi.write_readinto(read_register_address, write_register_address)
            self.ss_pin.value = True
        finally:
            self.spi.unlock()

    # ---- Read Only Interaction ----
    def read_register(self, register_address, length=1):
        while not self.spi.try_lock():
            pass
        try:
            self.spi.configure(self.baudrate, self.polarity, self.phase)
            self.ss_pin.value = False
            self.spi.readinto(register_address)
            self.ss_pin.value = True
        finally:
            self.spi.unlock()

    # ---- Write Only Interaction ----
    def write_register(self, register_address):
            while not self.spi.try_lock():
                pass
            try:
                self.spi.configure(self.baudrate, self.polarity, self.phase)
                self.ss_pin.value = False
                self.spi.write(register_address)
                self.ss_pin.value = True
            finally:
                self.spi.unlock()
    
    # ---- Sensor Data Conversion ----
    def read_gauss(self):
        # Read the 6 bytes of magnetic data
        mag_data = bytearray(6)
        self.read_register(mag_data, length=6)
        
        x_raw = (mag_data[0] << 8) | mag_data[1]
        y_raw = (mag_data[2] << 8) | mag_data[3]
        z_raw = (mag_data[4] << 8) | mag_data[5]

        x = (x_raw - NULL_FIELD_16BIT) / COUNTS_PER_GAUSS_16BIT
        y = (y_raw - NULL_FIELD_16BIT) / COUNTS_PER_GAUSS_16BIT
        z = (z_raw - NULL_FIELD_16BIT) / COUNTS_PER_GAUSS_16BIT

        return (x, y, z)
