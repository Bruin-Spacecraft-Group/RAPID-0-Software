"""
Gyroscope-only driver for the Bosch BMI088 (gyro die only), without adafruit_bus_device.SPIDevice.

- Uses busio.SPI directly with manual CS toggling and try_lock()/configure()/unlock
- Async-friendly (awaitable methods)
- Only the gyro die is touched (no accelerometer/temperature paths)
"""

#from Adafruit_CircuitPython_asyncio 
import asyncio
import time
import digitalio
import busio

# ----------------------------
# BMI088 GYROSCOPE REGISTERS
# ----------------------------
_SOFTRESET_CMD = 0xB6
_WRITE_DELAY_S = 0.0002

GYR_CHIP_ID_REG = 0x00
GYR_CHIP_ID_VAL = 0x0F

GYR_RANGE_REG = 0x0F
GYR_BW_REG    = 0x10
GYR_LPM1      = 0x11
GYR_SOFTRESET = 0x14
GYR_SELF_TEST = 0x3C
GYR_FIFO_STATUS = 0x0E
GYR_FIFO_CONFIG0 = 0x3D
GYR_FIFO_CONFIG1 = 0x3E

GYR_FIFO_MODE_MASK = 0xC0
GYR_FIFO_FRAME_COUNT_MASK = 0x7F

GYR_DATA_START = 0x02  # X_LSB, X_MSB, Y_LSB, Y_MSB, Z_LSB, Z_MSB

GYR_SELF_TEST_TRIG_BIT = 0x01  # bit0
GYR_SELF_TEST_BIT1 = 0x02      # bit1
GYR_SELF_TEST_BIT2 = 0x04      # bit2
GYR_SELF_TEST_BIT4 = 0x08      # bit3 (function status)

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

    def __init__(
        self,
        spi: busio.SPI,
        cs_gyro_pin_or_dio,
        *,
        baudrate=1600,
        polarity=0,
        phase=0,
        read_dummy_bytes=0,
        cs_active_low=True,
    ):
        self._spi = spi
        self._baudrate = baudrate
        self._polarity = polarity
        self._phase = phase
        self._read_dummy_bytes = 0 if read_dummy_bytes < 0 else int(read_dummy_bytes)
        self._cs_active_low = bool(cs_active_low)

        # Accept either a pin object or a pre-made DigitalInOut
        if isinstance(cs_gyro_pin_or_dio, digitalio.DigitalInOut):
            self._cs = cs_gyro_pin_or_dio
            self._cs.direction = digitalio.Direction.OUTPUT
            self._cs.value = not self._cs_active_low
            self._owns_cs = False
        else:
            self._cs = digitalio.DigitalInOut(cs_gyro_pin_or_dio)
            self._cs.direction = digitalio.Direction.OUTPUT
            self._cs.value = not self._cs_active_low
            self._owns_cs = True

        self.gyro_range = GyroRange.RANGE_125DPS

    def deinit(self):
        # Free the CS pin if we created it
        if getattr(self, "_owns_cs", False) and hasattr(self._cs, "deinit"):
            self._cs.deinit()
    # -------- Public API --------
    async def begin(self, *, verify_chip_id=False) -> bool:
        """
        Initialize ONLY the gyro die:
        - Soft-reset
        - Check chip ID
        - Power to normal mode
        - Apply default ODR/range
        """
        self._write_reg_gyro(GYR_SOFTRESET, _SOFTRESET_CMD)
        await asyncio.sleep(0.05)
        chip_id = self._read_reg_gyro(GYR_CHIP_ID_REG)

        if verify_chip_id and chip_id != GYR_CHIP_ID_VAL:
            await asyncio.sleep(0.01)
            chip_id = self._probe_chip_id()
            if chip_id != GYR_CHIP_ID_VAL:
                chip_id = self._probe_spi_mode()
            if chip_id != GYR_CHIP_ID_VAL:
                raise RuntimeError(f"BMI088 gyro: invalid chip ID 0x{chip_id:02X}")

        # Normal mode
        self._write_reg_gyro(GYR_LPM1, 0x00)
        await asyncio.sleep(0.002)

        # Reset/flush FIFO at startup.
        await self.reset_fifo()

        # Defaults: 400 Hz ODR, ±1000 dps
        await self.set_gyro_range(GyroRange.RANGE_125DPS)
        await self.set_gyro_odr(GyroODR.ODR_400HZ)
        return True

    async def reset_fifo(self):
        """
        Reset/flush gyro FIFO by forcing bypass mode at startup.
        """
        # Disable watermark/tag.
        self._write_reg_gyro(GYR_FIFO_CONFIG0, 0x00)

        # Force FIFO mode bits [7:6] to 00 (bypass).
        cfg1 = self._read_reg_gyro(GYR_FIFO_CONFIG1)
        self._write_reg_gyro(GYR_FIFO_CONFIG1, cfg1 & (~GYR_FIFO_MODE_MASK & 0xFF))
        await asyncio.sleep(0.002)

        # Return frame count after flush request.
        status = self._read_reg_gyro(GYR_FIFO_STATUS)
        return status & GYR_FIFO_FRAME_COUNT_MASK

    async def read_gyro_raw(self):
        """
        Raw angular rate (int16) in LSB for X,Y,Z.
        """
        buf = self._read_block_gyro(GYR_DATA_START, 6)
        if self._read_dummy_bytes > 0:
            # For the current wiring/transaction framing, dummy-byte reads need
            # swapped byte order per 16-bit axis sample.
            x = _to_int16(buf[0], buf[1])
            y = _to_int16(buf[2], buf[3])
            z = _to_int16(buf[4], buf[5])
        else:
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

    async def self_test_gyro(self, wait_s=0.05, timeout_s=100):
        """
        Trigger gyro self-test by writing bit0 of 0x3C, then read back bits 1/2/4.
        Returns a dict with the raw register and requested bit values.
        """
        # Datasheet self-test trigger: write bit0 = 1.
        self._write_reg_gyro(GYR_SELF_TEST, GYR_SELF_TEST_TRIG_BIT)
        await asyncio.sleep(wait_s)

        t_end = time.monotonic() + timeout_s
        result = self._read_reg_gyro(GYR_SELF_TEST)
        while (result & GYR_SELF_TEST_BIT1) == 0 and time.monotonic() < t_end:
            #await asyncio.sleep(0.01)
            result = self._read_reg_gyro(GYR_SELF_TEST)

        return {
            "raw_0x3C": result,
            "bit1": 1 if (result & GYR_SELF_TEST_BIT1) else 0,
            "bit2": 1 if (result & GYR_SELF_TEST_BIT2) else 0,
            "bit4": 1 if (result & GYR_SELF_TEST_BIT4) else 0,
            "timed_out": 1 if (result & GYR_SELF_TEST_BIT1) == 0 else 0,
        }

    # -------- Internal helpers --------
    def _read_reg_gyro(self, reg: int) -> int:
        return self._read_block_gyro(reg, 1)[0]

    def _write_reg_gyro(self, reg: int, value: int):
        self._write_block(reg, bytes([value & 0xFF]))

    def _read_block_gyro(self, start_reg: int, length: int) -> bytes:
        return self._read_block(start_reg, length)

    def _probe_chip_id(self) -> int:
        original_dummy = self._read_dummy_bytes
        chip_id = self._read_reg_gyro(GYR_CHIP_ID_REG)
        if chip_id == GYR_CHIP_ID_VAL:
            return chip_id
        self._read_dummy_bytes = 0
        chip_id = self._read_reg_gyro(GYR_CHIP_ID_REG)
        if chip_id != GYR_CHIP_ID_VAL:
            self._read_dummy_bytes = original_dummy
        return chip_id

    def _probe_spi_mode(self) -> int:
        original = (self._polarity, self._phase)
        chip_id = self._read_reg_gyro(GYR_CHIP_ID_REG)
        if chip_id == GYR_CHIP_ID_VAL:
            return chip_id
        for pol, ph in ((0, 0), (1, 1)):
            self._polarity, self._phase = pol, ph
            chip_id = self._probe_chip_id()
            if chip_id == GYR_CHIP_ID_VAL:
                return chip_id
        self._polarity, self._phase = original
        return chip_id

    @staticmethod
    def _build_read_command(reg: int) -> int:
        # BMI088 SPI: MSB=1 for read
        return (reg & 0x7F) | 0x80

    @staticmethod
    def _build_write_command(reg: int) -> int:
        # MSB=0 for write
        return reg & 0x7F

    # ---- Raw SPI transactions (no SPIDevice) ----
    def _cs_select(self):
        self._cs.value = False if self._cs_active_low else True

    def _cs_deselect(self):
        self._cs.value = True if self._cs_active_low else False

    def _spi_tx(self, tx: bytearray):
        # Write-only transaction
        while not self._spi.try_lock():
            pass
        try:
            self._spi.configure(baudrate=self._baudrate, polarity=self._polarity, phase=self._phase)
            self._cs_select()
            self._spi.write(tx)
        finally:
            self._cs_deselect()
            self._spi.unlock()
        # Give the gyro a short settle time after register writes.
        time.sleep(_WRITE_DELAY_S)

    def _spi_txrx(self, tx: bytearray, rx: bytearray):
        # Full-duplex transaction
        while not self._spi.try_lock():
            pass
        try:
            self._spi.configure(baudrate=self._baudrate, polarity=self._polarity, phase=self._phase)
            self._cs_select()
            self._spi.write_readinto(tx, rx)
        finally:
            self._cs_deselect()
            self._spi.unlock()

    def _read_block(self, start_reg: int, length: int) -> bytes:
        # Full-duplex read transfer:
        # [command][optional dummy bytes][payload bytes]
        header_len = 1 + self._read_dummy_bytes
        transfer_len = header_len + length
        out_buf = bytearray(transfer_len)
        in_buf = bytearray(transfer_len)
        out_buf[0] = self._build_read_command(start_reg)

        while not self._spi.try_lock():
            pass
        try:
            self._spi.configure(
                baudrate=self._baudrate, polarity=self._polarity, phase=self._phase
            )
            self._cs_select()
            self._spi.write_readinto(out_buf, in_buf)
        finally:
            self._cs_deselect()
            self._spi.unlock()

        return in_buf[header_len:]

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

