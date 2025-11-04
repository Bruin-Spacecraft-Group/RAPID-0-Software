"""
Driver module for the Bosch BMI088 6-axis IMU (accelerometer + gyroscope).
Asynchronous, CircuitPython-style implementation for CMU robotics systems.
"""

import time
import asyncio
import digitalio
import busio


class AccelRange:
    RANGE_3G = 0x00
    RANGE_6G = 0x01
    RANGE_12G = 0x02
    RANGE_24G = 0x03


class GyroRange:
    RANGE_2000DPS = 0x00
    RANGE_1000DPS = 0x01
    RANGE_500DPS = 0x02
    RANGE_250DPS = 0x03
    RANGE_125DPS = 0x04


class AccelODR:
    ODR_100HZ = 0x0D
    ODR_400HZ = 0x07
    ODR_1600HZ = 0x04


class GyroODR:
    ODR_100HZ = 0x87
    ODR_400HZ = 0x83
    ODR_1000HZ = 0x82
    ODR_2000HZ = 0x80


ACC_REG_DATA = 0x12
GYRO_REG_DATA = 0x02
TEMP_REG = 0x22

# Conversion constants
ACC_SCALE = {
    AccelRange.RANGE_3G: 9.807 / 1024,
    AccelRange.RANGE_6G: 9.807 / 512,
    AccelRange.RANGE_12G: 9.807 / 256,
    AccelRange.RANGE_24G: 9.807 / 128,
}
GYRO_SCALE = {
    GyroRange.RANGE_2000DPS: 2000.0 / 32768.0,
    GyroRange.RANGE_1000DPS: 1000.0 / 32768.0,
    GyroRange.RANGE_500DPS: 500.0 / 32768.0,
    GyroRange.RANGE_250DPS: 250.0 / 32768.0,
    GyroRange.RANGE_125DPS: 125.0 / 32768.0,
}
GYRO_D2R = 3.141592653589793 / 180.0


class Bmi088:
    """
    Asynchronous CircuitPython driver for the Bosch BMI088 IMU.
    Reads accelerometer, gyroscope, and temperature data via SPI.
    """

    def __init__(self, spi_bus, cs_accel, cs_gyro):
        self.spi = spi_bus

        # Accelerometer CS
        self.cs_accel = digitalio.DigitalInOut(cs_accel)
        self.cs_accel.direction = digitalio.Direction.OUTPUT
        self.cs_accel.value = True

        # Gyroscope CS
        self.cs_gyro = digitalio.DigitalInOut(cs_gyro)
        self.cs_gyro.direction = digitalio.Direction.OUTPUT
        self.cs_gyro.value = True

        self.accel_range = AccelRange.RANGE_6G
        self.gyro_range = GyroRange.RANGE_1000DPS

    def _spi_write_read(self, cs_pin, tx_bytes, rx_bytes):
        """Low-level SPI helper."""
        while not self.spi.try_lock():
            pass
        try:
            self.spi.configure(baudrate=1000000, polarity=0, phase=0)
            cs_pin.value = False
            self.spi.write_readinto(tx_bytes, rx_bytes)
            cs_pin.value = True
        finally:
            self.spi.unlock()

    async def begin(self):
        """
        Initializes the BMI088 sensors.
        Sends soft reset and waits for ready.
        """
        # Reset both sensors
        await self._soft_reset()
        await asyncio.sleep(0.05)
        # Could check chip IDs here if desired
        return True

    async def _soft_reset(self):
        """Send soft reset command."""
        reset_cmd = bytes([0x7E & 0x7F, 0xB6])
        dummy = bytearray(2)
        self._spi_write_read(self.cs_accel, reset_cmd, dummy)
        self._spi_write_read(self.cs_gyro, reset_cmd, dummy)

    async def read_accel(self):
        """Reads acceleration (m/s^2) in X,Y,Z."""
        tx = bytes([ACC_REG_DATA | 0x80, 0, 0, 0, 0, 0, 0])
        rx = bytearray(len(tx))
        self._spi_write_read(self.cs_accel, tx, rx)
        x = self._to_int16(rx[1], rx[2])
        y = self._to_int16(rx[3], rx[4])
        z = self._to_int16(rx[5], rx[6])
        scale = ACC_SCALE[self.accel_range]
        return (x * scale, y * scale, z * scale)

    async def read_gyro(self):
        """Reads angular rate (rad/s) in X,Y,Z."""
        tx = bytes([GYRO_REG_DATA | 0x80, 0, 0, 0, 0, 0, 0])
        rx = bytearray(len(tx))
        self._spi_write_read(self.cs_gyro, tx, rx)
        x = self._to_int16(rx[1], rx[2])
        y = self._to_int16(rx[3], rx[4])
        z = self._to_int16(rx[5], rx[6])
        dps_scale = GYRO_SCALE[self.gyro_range]
        return (
            x * dps_scale * GYRO_D2R,
            y * dps_scale * GYRO_D2R,
            z * dps_scale * GYRO_D2R,
        )

    async def read_temperature(self):
        """Reads temperature in °C."""
        tx = bytes([TEMP_REG | 0x80, 0, 0])
        rx = bytearray(len(tx))
        self._spi_write_read(self.cs_accel, tx, rx)
        raw = self._to_int16(rx[1], rx[2])
        return 23.0 + raw / 512.0  # datasheet linearization

    async def read_all(self):
        """Convenience coroutine to read accel, gyro, and temp together."""
        a = await self.read_accel()
        g = await self.read_gyro()
        t = await self.read_temperature()
        return {"accel_mss": a, "gyro_rads": g, "temp_C": t}

    @staticmethod
    def _to_int16(msb, lsb):
        val = (msb << 8) | lsb
        if val & 0x8000:
            val -= 65536
        return val