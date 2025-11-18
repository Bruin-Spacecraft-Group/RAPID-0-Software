"""
Gyroscope-only driver for the Bosch BMI088 (gyro die only), without adafruit_bus_device.SPIDevice.

- Uses busio.SPI directly with manual CS toggling and try_lock()/configure()/unlock
- Async-friendly (awaitable methods)
- Only the gyro die is touched (no accelerometer/temperature paths)
"""

from Adafruit_CircuitPython_asyncio import asyncio
import digitalio
import busio

# ----------------------------
# BMI088 GYROSCOPE REGISTERS
# ----------------------------
_SOFTRESET_CMD = 0xB6

GYR_CHIP_ID_REG = 0x00
GYR_CHIP_ID_VAL = 0x0F

GYR_RANGE_REG = 0x0F
GYR_BW_REG    = 0x10
GYR_LPM1      = 0x11
GYR_SOFTRESET = 0x14

GYR_DATA_START = 0x02  # X_LSB, X_MSB, Y_LSB, Y_MSB, Z_LSB, Z_MSB

# ----------------------------
# CONFIG ENUMS
# ----------------------------
class GyroRange:
    RANGE_2000DPS = 0x00
    RANGE_1000DPS = 0x01
    RANGE_500DPS  = 0x02
    RANGE_250DPS  = 0x03
    RANGE_125DPS  = 0x04

class GyroODR:
    # Encoded in GYR_BW; symbolic mapping
    ODR_100HZ  = 0x07
    ODR_200HZ  = 0x06
    ODR_400HZ  = 0x05
    ODR_1000HZ = 0x03
    ODR_2000HZ = 0x01

# ----------------------------
# SCALING CONSTANTS
# ----------------------------
GYRO_SCALE_DPS = {
    GyroRange.RANGE_2000DPS: 2000.0 / 32768.0,
    GyroRange.RANGE_1000DPS: 1000.0 / 32768.0,
    GyroRange.RANGE_500DPS:   500.0 / 32768.0,
    GyroRange.RANGE_250DPS:   250.0 / 32768.0,
    GyroRange.RANGE_125DPS:   125.0 / 32768.0,
}
DEG2RAD = 3.141592653589793 / 180.0

# ----------------------------
# DRIVER (GYRO ONLY)
# ----------------------------
class Bmi088Gyro:
    """
    Gyro-only BMI088 driver.

    Usage:
        import busio
        from bmi088 import Bmi088Gyro, GyroRange, GyroODR
        spi = busio.SPI(SCK, MOSI=MOSI, MISO=MISO)
        gyro = Bmi088Gyro(spi, cs_gyro_pin=CS_PIN)
        await gyro.begin()
        gx, gy, gz = await gyro.read_gyro()
    """

    def __init__(self, spi: busio.SPI, cs_gyro_pin, *, baudrate=1_000_000, polarity=0, phase=0):
        self._spi = spi
        self._baudrate = baudrate
        self._polarity = polarity
        self._phase = phase

        # Chip-select for the gyro die (CSB2)
        self._cs = digitalio.DigitalInOut(cs_gyro_pin)
        self._cs.direction = digitalio.Direction.OUTPUT
        self._cs.value = True  # inactive high

        self.gyro_range = GyroRange.RANGE_1000DPS  # default scale

    # -------- Public API --------
    async def begin(self) -> bool:
        """
        Initialize ONLY the gyro die:
        - Soft-reset
        - Check chip ID
        - Power to normal mode
        - Apply default ODR/range
        """
        self._write_reg_gyro(GYR_SOFTRESET, _SOFTRESET_CMD)
        await asyncio.sleep(0.05)

        if self._read_reg_gyro(GYR_CHIP_ID_REG) != GYR_CHIP_ID_VAL:
            raise RuntimeError("BMI088 gyro: invalid chip ID")

        # Normal mode
        self._write_reg_gyro(GYR_LPM1, 0x00)

        # Defaults: 400 Hz ODR, ±1000 dps
        await self.set_gyro_range(GyroRange.RANGE_1000DPS)
        await self.set_gyro_odr(GyroODR.ODR_400HZ)
        return True

    async def read_gyro_raw(self):
        """
        Raw angular rate (int16) in LSB for X,Y,Z.
        """
        buf = self._read_block_gyro(GYR_DATA_START, 6)
        x = _to_int16(buf[1], buf[0])
        y = _to_int16(buf[3], buf[2])
        z = _to_int16(buf[5], buf[4])
        return x, y, z

    async def read_gyro(self):
        """
        Angular rate in rad/s for X,Y,Z.
        """
        x, y, z = await self.read_gyro_raw()
        dps_scale = GYRO_SCALE_DPS[self.gyro_range]
        return (
            x * dps_scale * DEG2RAD,
            y * dps_scale * DEG2RAD,
            z * dps_scale * DEG2RAD,
        )

    async def set_gyro_odr(self, odr):
        """
        Set gyro ODR/bandwidth (symbolic).
        new = (current & 0xF0) | (odr & 0x0F)
        """
        current = self._read_reg_gyro(GYR_BW_REG)
        self._write_reg_gyro(GYR_BW_REG, (current & 0xF0) | (odr & 0x0F))

    async def set_gyro_range(self, gyro_range):
        """
        Set gyro full-scale range.
        """
        self._write_reg_gyro(GYR_RANGE_REG, gyro_range & 0x07)
        self.gyro_range = gyro_range

    # -------- Internal helpers --------
    def _read_reg_gyro(self, reg: int) -> int:
        return self._read_block_gyro(reg, 1)[0]

    def _write_reg_gyro(self, reg: int, value: int):
        self._write_block(reg, bytes([value & 0xFF]))

    def _read_block_gyro(self, start_reg: int, length: int) -> bytes:
        return self._read_block(start_reg, length)

    @staticmethod
    def _build_read_command(reg: int) -> int:
        # BMI088 SPI: MSB=1 for read
        return (reg & 0x7F) | 0x80

    @staticmethod
    def _build_write_command(reg: int) -> int:
        # MSB=0 for write
        return reg & 0x7F

    # ---- Raw SPI transactions (no SPIDevice) ----
    def _spi_tx(self, tx: bytearray):
        # Write-only transaction
        while not self._spi.try_lock():
            pass
        try:
            self._spi.configure(baudrate=self._baudrate, polarity=self._polarity, phase=self._phase)
            self._cs.value = False
            self._spi.write(tx)
            self._cs.value = True
        finally:
            self._spi.unlock()

    def _spi_txrx(self, tx: bytearray, rx: bytearray):
        # Full-duplex transaction
        while not self._spi.try_lock():
            pass
        try:
            self._spi.configure(baudrate=self._baudrate, polarity=self._polarity, phase=self._phase)
            self._cs.value = False
            self._spi.write_readinto(tx, rx)
            self._cs.value = True
        finally:
            self._spi.unlock()

    def _read_block(self, start_reg: int, length: int) -> bytes:
        out_buf = bytearray(length + 1)
        in_buf  = bytearray(length + 1)
        out_buf[0] = self._build_read_command(start_reg)
        self._spi_txrx(out_buf, in_buf)
        return in_buf[1:]  # strip command echo

    def _write_block(self, reg: int, data: bytes):
        out_buf = bytearray(1 + len(data))
        out_buf[0] = self._build_write_command(reg)
        out_buf[1:] = data
        self._spi_tx(out_buf)

# ----------------------------
# Utilities
# ----------------------------
def _to_int16(msb: int, lsb: int) -> int:
    val = (msb << 8) | lsb
    if val & 0x8000:
        val -= 0x10000
    return val

