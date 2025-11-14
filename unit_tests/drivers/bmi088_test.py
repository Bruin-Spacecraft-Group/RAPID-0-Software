import unittest
import asyncio
from unittest import mock

# Import the gyro-only driver module and use its names
import Bmi088Gyro as bmi088


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class BMI088GyroTest(unittest.TestCase):
    def setUp(self):
        # Build an instance without calling __init__ (no real SPI needed)
        self.gyro = bmi088.Bmi088Gyro.__new__(bmi088.Bmi088Gyro)
        self.gyro.gyro_range = bmi088.GyroRange.RANGE_1000DPS

    # ----- Low-level helpers -----

    def test_build_read_write_commands(self):
        self.assertEqual(bmi088.Bmi088Gyro._build_read_command(0x00), 0x80)
        self.assertEqual(bmi088.Bmi088Gyro._build_read_command(0x12), 0x92)
        self.assertEqual(bmi088.Bmi088Gyro._build_write_command(0x00), 0x00)
        self.assertEqual(bmi088.Bmi088Gyro._build_write_command(0x7E), 0x7E)
        self.assertEqual(bmi088.Bmi088Gyro._build_write_command(0x80), 0x00)  # MSB cleared

    def test_to_int16(self):
        self.assertEqual(bmi088._to_int16(0x00, 0x00), 0)
        self.assertEqual(bmi088._to_int16(0x7F, 0xFF), 32767)
        self.assertEqual(bmi088._to_int16(0x80, 0x00), -32768)
        self.assertEqual(bmi088._to_int16(0xFF, 0xFF), -1)
        self.assertEqual(bmi088._to_int16(0x01, 0x00), 256)
        self.assertEqual(bmi088._to_int16(0xFE, 0x00), -512)

    # ----- Begin / chip ID -----

    def test_begin_ok_calls(self):
        with mock.patch.object(self.gyro, "_read_reg_gyro", return_value=bmi088.GYR_CHIP_ID_VAL), \
             mock.patch.object(self.gyro, "_write_reg_gyro") as wr, \
             mock.patch.object(self.gyro, "set_gyro_range", new=mock.AsyncMock()) as sgr, \
             mock.patch.object(self.gyro, "set_gyro_odr",   new=mock.AsyncMock()) as sgo:
            run(self.gyro.begin())
            # soft reset then normal mode + default config
            wr.assert_any_call(bmi088.GYR_SOFTRESET, bmi088._SOFTRESET_CMD)
            wr.assert_any_call(bmi088.GYR_LPM1, 0x00)
            sgr.assert_awaited()
            sgo.assert_awaited()

    def test_begin_bad_chipid_raises(self):
        with mock.patch.object(self.gyro, "_read_reg_gyro", return_value=0xFF):
            with self.assertRaises(RuntimeError):
                run(self.gyro.begin())

    # ----- Setters -----

    def test_set_gyro_odr_masks_bits(self):
        # new = (current & 0xF0) | (odr & 0x0F)
        with mock.patch.object(self.gyro, "_read_reg_gyro", return_value=0x3C), \
             mock.patch.object(self.gyro, "_write_reg_gyro") as wr:
            run(self.gyro.set_gyro_odr(bmi088.GyroODR.ODR_100HZ))  # 0x07
            wr.assert_called_once_with(bmi088.GYR_BW_REG, 0x37)    # (0x3C & 0xF0)=0x30 | 0x07

    def test_set_gyro_range_updates_cache(self):
        with mock.patch.object(self.gyro, "_write_reg_gyro") as wr:
            run(self.gyro.set_gyro_range(bmi088.GyroRange.RANGE_250DPS))
            wr.assert_called_once_with(bmi088.GYR_RANGE_REG, bmi088.GyroRange.RANGE_250DPS & 0x07)
            self.assertEqual(self.gyro.gyro_range, bmi088.GyroRange.RANGE_250DPS)

    # ----- Data path -----

    def test_read_gyro_scaling(self):
        self.gyro.gyro_range = bmi088.GyroRange.RANGE_1000DPS
        with mock.patch.object(self.gyro, "read_gyro_raw", new=mock.AsyncMock(return_value=(32767, 0, -32768))):
            gx, gy, gz = run(self.gyro.read_gyro())
            self.assertAlmostEqual(gx, (1000.0/32768.0*32767) * bmi088.DEG2RAD, places=5)
            self.assertAlmostEqual(gy, 0.0, places=9)
            self.assertAlmostEqual(gz, (-1000.0/32768.0*32768) * bmi088.DEG2RAD, places=5)

    # ----- Register plumbing sanity -----

    def test_read_reg_uses_block(self):
        with mock.patch.object(self.gyro, "_read_block_gyro", return_value=bytes([0xCD])):
            self.assertEqual(self.gyro._read_reg_gyro(0x10), 0xCD)


if __name__ == "__main__":
    unittest.main()
