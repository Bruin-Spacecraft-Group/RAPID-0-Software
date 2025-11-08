"""
Driver module for the Bosch BMI088 6-axis IMU (accelerometer + gyroscope).

- Uses busio.SPI and adafruit_bus_device.SPIDevice for clean SPI handling.
- Async-friendly API (methods are `async` so they drop into an asyncio event loop).
- Inspired by STM32 C driver structure (chip ID check, power/ODR/range setup).
"""

import asyncio
import digitalio
import busio
from adafruit_bus_device.spi_device import SPIDevice


# ---------------------------------------------------------------------------
# BMI088 register map (minimal subset; verify against datasheet for production)
# ---------------------------------------------------------------------------

# Common
_SOFTRESET_CMD = 0xB6

# Accelerometer (ACC)
ACC_CHIP_ID_REG = 0x00
ACC_CHIP_ID_VAL = 0x1E  # per BMI088 datasheet

ACC_ERR_REG = 0x02  # optional, for diagnostics

ACC_TEMP_MSB = 0x22  # temp high byte (MSB), LSB at 0x23
ACC_DATA_START = 0x12  # X_LSB at 0x12, then X_MSB, Y_LSB, ...

ACC_PWR_CONF = 0x7C
ACC_PWR_CTRL = 0x7D
ACC_SOFTRESET = 0x7E

ACC_CONF = 0x40
ACC_RANGE_REG = 0x41

# Gyroscope (GYR)
GYR_CHIP_ID_REG = 0x00
GYR_CHIP_ID_VAL = 0x0F  # per BMI088 datasheet

GYR_RANGE_REG = 0x0F
GYR_BW_REG = 0x10
GYR_LPM1 = 0x11
GYR_SOFTRESET = 0x14

GYR_DATA_START = 0x02  # X_LSB at 0x02, etc.

# ---------------------------------------------------------------------------
# Configuration enums (bitfield values, keep aligned with datasheet)
# ---------------------------------------------------------------------------

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
    # Encoded in ACC_CONF high bits; check datasheet if you change
    ODR_12_5HZ = 0x05
    ODR_25HZ = 0x06
    ODR_50HZ = 0x07
    ODR_100HZ = 0x08
    ODR_200HZ = 0x09
    ODR_400HZ = 0x0A
    ODR_800HZ = 0x0B
    ODR_1600HZ = 0x0C


class GyroODR:
    # Encoded in GYR_BW; symbolic, you can map exactly if needed
    ODR_100HZ = 0x07
    ODR_200HZ = 0x06
    ODR_400HZ = 0x05
    ODR_1000HZ = 0x03
    ODR_2000HZ = 0x01


# ---------------------------------------------------------------------------
# Conversion constants (LSB → physical units)
# (Values assume standard BMI088 scaling; adjust if you change modes)
# ---------------------------------------------------------------------------

ACC_SCALE = {
    AccelRange.RANGE_3G: 9.807 / 1024.0,
    AccelRange.RANGE_6G: 9.807 / 512.0,
    AccelRange.RANGE_12G: 9.807 / 256.0,
    AccelRange.RANGE_24G: 9.807 / 128.0,
}

GYRO_SCALE_DPS = {
    GyroRange.RANGE_2000DPS: 2000.0 / 32768.0,
    GyroRange.RANGE_1000DPS: 1000.0 / 32768.0,
    GyroRange.RANGE_500DPS: 500.0 / 32768.0,
    GyroRange.RANGE_250DPS: 250.0 / 32768.0,
    GyroRange.RANGE_125DPS: 125.0 / 32768.0,
}

DEG2RAD = 3.141592653589793 / 180.0


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

class Bmi088:
    """
    BMI088 driver using SPIDevice for simple, robust SPI handling.

    Usage:

        import board, busio, digitalio
        from adafruit_bus_device.spi_device import SPIDevice

        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        cs_accel = digitalio.DigitalInOut(board.D5)
        cs_gyro = digitalio.DigitalInOut(board.D6)

        imu = Bmi088(spi, cs_accel, cs_gyro)
        await imu.begin()
        data = await imu.read_all()
    """

    def __init__(self, spi: busio.SPI, cs_accel_pin, cs_gyro_pin):
        # Configure CS pins as DigitalInOut
        self._cs_accel = digitalio.DigitalInOut(cs_accel_pin)
        self._cs_accel.direction = digitalio.Direction.OUTPUT
        self._cs_accel.value = True

        self._cs_gyro = digitalio.DigitalInOut(cs_gyro_pin)
        self._cs_gyro.direction = digitalio.Direction.OUTPUT
        self._cs_gyro.value = True

        # Two SPIDevice instances share same SPI bus, different CS
        self._accel_dev = SPIDevice(
            spi,
            self._cs_accel,
            baudrate=1_000_000,
            polarity=0,
            phase=0,
        )
        self._gyro_dev = SPIDevice(
            spi,
            self._cs_gyro,
            baudrate=1_000_000,
            polarity=0,
            phase=0,
        )

        # Config cache (used for scaling)
        self.accel_range = AccelRange.RANGE_6G
        self.gyro_range = GyroRange.RANGE_2000DPS

    # ---------------------- Public API -------------------------------------

    async def begin(self) -> bool:
        """
        Initialize BMI088:
        - Soft reset both sensors
        - Check chip IDs
        - Power up accel & gyro
        - Apply default ODR and ranges
        """
        await self.soft_reset()
        await asyncio.sleep(0.05)

        if not self._check_chip_ids():
            raise RuntimeError("BMI088: invalid chip ID(s)")

        # Power up accel (normal mode)
        # ACC_PWR_CONF: 0x00  => no deep-suspend
        # ACC_PWR_CTRL: bit0=ACC_EN
        self._write_reg_accel(ACC_PWR_CONF, 0x00)
        self._write_reg_accel(ACC_PWR_CTRL, 0x04)  # datasheet: ACC_EN bit

        # Power up gyro: GYR_LPM1: normal mode (0x00 or 0x01 depending on bits)
        self._write_reg_gyro(GYR_LPM1, 0x00)

        # Default config: 100 Hz accel, ±6g; 100 Hz gyro, ±2000 dps
        await self.set_accel_odr(AccelODR.ODR_100HZ)
        await self.set_accel_range(AccelRange.RANGE_6G)
        await self.set_gyro_range(GyroRange.RANGE_2000DPS)
        await self.set_gyro_odr(GyroODR.ODR_100HZ)

        return True

    async def soft_reset(self):
        """Soft reset accel and gyro blocks."""
        self._write_reg_accel(ACC_SOFTRESET, _SOFTRESET_CMD)
        self._write_reg_gyro(GYR_SOFTRESET, _SOFTRESET_CMD)

    async def read_accel_raw(self):
        """
        Read raw accelerometer data (int16) for X, Y, Z.
        """
        buf = self._read_block_accel(ACC_DATA_START, 6)
        x = _to_int16(buf[1], buf[0])
        y = _to_int16(buf[3], buf[2])
        z = _to_int16(buf[5], buf[4])
        return x, y, z

    async def read_gyro_raw(self):
        """
        Read raw gyroscope data (int16) for X, Y, Z.
        """
        buf = self._read_block_gyro(GYR_DATA_START, 6)
        x = _to_int16(buf[1], buf[0])
        y = _to_int16(buf[3], buf[2])
        z = _to_int16(buf[5], buf[4])
        return x, y, z

    async def read_accel(self):
        """
        Read accelerometer in m/s^2 (X, Y, Z).
        """
        x, y, z = await self.read_accel_raw()
        scale = ACC_SCALE[self.accel_range]
        return x * scale, y * scale, z * scale

    async def read_gyro(self):
        """
        Read gyroscope in rad/s (X, Y, Z).
        """
        x, y, z = await self.read_gyro_raw()
        dps_scale = GYRO_SCALE_DPS[self.gyro_range]
        return (
            x * dps_scale * DEG2RAD,
            y * dps_scale * DEG2RAD,
            z * dps_scale * DEG2RAD,
        )

    async def read_temperature_raw(self):
        """
        Read raw temperature (int16).
        Uses accel temperature registers.
        """
        buf = self._read_block_accel(ACC_TEMP_MSB, 2)
        return _to_int16(buf[0], buf[1])

    async def read_temperature(self):
        """
        Read temperature in °C.
        Formula is approximate; verify with datasheet for your mode.
        """
        raw = await self.read_temperature_raw()
        # Common linearization used for BMI088 accel temp sensor
        return 23.0 + raw / 512.0

    async def read_all(self):
        """
        Convenience: read accel (m/s^2), gyro (rad/s), and temp (°C).
        """
        ax, ay, az = await self.read_accel()
        gx, gy, gz = await self.read_gyro()
        t = await self.read_temperature()
        return {
            "accel_mss": (ax, ay, az),
            "gyro_rads": (gx, gy, gz),
            "temp_C": t,
        }

    # ------------------- Configuration setters -----------------------------

    async def set_accel_odr(self, odr):
        """
        Set accelerometer ODR (see AccelODR).
        ODR bits live in ACC_CONF[7:4]; low nibble often bandwidth.
        Here we just overwrite the upper bits cleanly.
        """
        current = self._read_reg_accel(ACC_CONF)
        new_val = (current & 0x0F) | ((odr & 0x0F) << 4)
        self._write_reg_accel(ACC_CONF, new_val)

    async def set_gyro_odr(self, odr):
        """
        Set gyro ODR/bandwidth (symbolic).
        Implementation keeps lower bits, updates ODR bits.
        """
        current = self._read_reg_gyro(GYR_BW_REG)
        new_val = (current & 0xF0) | (odr & 0x0F)
        self._write_reg_gyro(GYR_BW_REG, new_val)

    async def set_accel_range(self, accel_range):
        """
        Set accelerometer full-scale range.
        """
        self._write_reg_accel(ACC_RANGE_REG, accel_range & 0x03)
        self.accel_range = accel_range

    async def set_gyro_range(self, gyro_range):
        """
        Set gyroscope full-scale range.
        """
        self._write_reg_gyro(GYR_RANGE_REG, gyro_range & 0x07)
        self.gyro_range = gyro_range

    # ------------------- Internal helpers ----------------------------------

    def _check_chip_ids(self) -> bool:
        acc_id = self._read_reg_accel(ACC_CHIP_ID_REG)
        gyr_id = self._read_reg_gyro(GYR_CHIP_ID_REG)
        return (acc_id == ACC_CHIP_ID_VAL) and (gyr_id == GYR_CHIP_ID_VAL)

    # --- Register read/write via SPIDevice (accel) ---

    def _read_reg_accel(self, reg: int) -> int:
        return self._read_block_accel(reg, 1)[0]

    def _write_reg_accel(self, reg: int, value: int):
        self._write_block(self._accel_dev, reg, bytes([value & 0xFF]))

    def _read_block_accel(self, start_reg: int, length: int) -> bytes:
        return self._read_block(self._accel_dev, start_reg, length)

    # --- Register read/write via SPIDevice (gyro) ---

    def _read_reg_gyro(self, reg: int) -> int:
        return self._read_block_gyro(reg, 1)[0]

    def _write_reg_gyro(self, reg: int, value: int):
        self._write_block(self._gyro_dev, reg, bytes([value & 0xFF]))

    def _read_block_gyro(self, start_reg: int, length: int) -> bytes:
        return self._read_block(self._gyro_dev, start_reg, length)

    # --- Generic SPI helpers ---

    @staticmethod
    def _build_read_command(reg: int) -> int:
        # BMI088 SPI: MSB=1 for read
        return (reg & 0x7F) | 0x80

    @staticmethod
    def _build_write_command(reg: int) -> int:
        # MSB=0 for write
        return reg & 0x7F

    def _read_block(self, device: SPIDevice, start_reg: int, length: int) -> bytes:
        """
        Read `length` bytes starting at `start_reg` from the given SPIDevice.
        """
        out_buf = bytearray(length + 1)
        in_buf = bytearray(length + 1)
        out_buf[0] = self._build_read_command(start_reg)

        with device as spi:
            spi.write_readinto(out_buf, in_buf)

        return in_buf[1:]  # skip command byte

    def _write_block(self, device: SPIDevice, reg: int, data: bytes):
        """
        Write `data` bytes starting at `reg` to the given SPIDevice.
        """
        out_buf = bytearray(1 + len(data))
        out_buf[0] = self._build_write_command(reg)
        out_buf[1:] = data

        with device as spi:
            spi.write(out_buf)


# ---------------------------------------------------------------------------
# Small helper for 16-bit signed conversion (like combine_bytes in C)
# ---------------------------------------------------------------------------

def _to_int16(msb: int, lsb: int) -> int:
    val = (msb << 8) | lsb
    if val & 0x8000:
        val -= 0x10000
    return val
