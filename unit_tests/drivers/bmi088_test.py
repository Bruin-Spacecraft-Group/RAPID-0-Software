import unittest
import asyncio
from unittest import mock

import bmi088


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class BMI088_Test(unittest.TestCase):
    def setUp(self):
        # Build a "raw" instance without running __init__ (so we don't need real SPI/pins)
        self.imu = bmi088.Bmi088.__new__(bmi088.Bmi088)
        # Provide minimal attributes used in tests
        # self.imu.accel_range = bmi088.AccelRange.RANGE_6G
        self.imu.gyro_range = bmi088.GyroRange.RANGE_1000DPS

    # --- Low-level helpers -------------------------------------------------

    def test_build_read_write_commands(self):
        # MSB=1 for read, MSB=0 for write
        self.assertEqual(bmi088.Bmi088._build_read_command(0x00), 0x80)
        self.assertEqual(bmi088.Bmi088._build_read_command(0x12), 0x92)
        self.assertEqual(bmi088.Bmi088._build_write_command(0x00), 0x00)
        self.assertEqual(bmi088.Bmi088._build_write_command(0x7E), 0x7E)
        # ensure MSB cleared on write even if passed with MSB set
        self.assertEqual(bmi088.Bmi088._build_write_command(0x80), 0x00)

    def test_to_int16(self):
        self.assertEqual(bmi088._to_int16(0x00, 0x00), 0)
        self.assertEqual(bmi088._to_int16(0x7F, 0xFF), 32767)
        self.assertEqual(bmi088._to_int16(0x80, 0x00), -32768)
        self.assertEqual(bmi088._to_int16(0xFF, 0xFF), -1)
        self.assertEqual(bmi088._to_int16(0x01, 0x00), 256)
        self.assertEqual(bmi088._to_int16(0xFE, 0x00), -512)

    # --- Chip ID check -----------------------------------------------------

    def test_check_chip_ids(self):
        # with mock.patch.object(self.imu, "_read_reg_accel", return_value=bmi088.ACC_CHIP_ID_VAL), \
        with mock.patch.object(self.imu, "_read_reg_gyro", return_value=bmi088.GYR_CHIP_ID_VAL):
            self.assertTrue(self.imu._check_chip_ids())

        # Wrong accel ID
        # with mock.patch.object(self.imu, "_read_reg_accel", return_value=0x00), \
        with mock.patch.object(self.imu, "_read_reg_gyro", return_value=bmi088.GYR_CHIP_ID_VAL):
            self.assertFalse(self.imu._check_chip_ids())

        # Wrong gyro ID
        # with mock.patch.object(self.imu, "_read_reg_accel", return_value=bmi088.ACC_CHIP_ID_VAL), \
        with mock.patch.object(self.imu, "_read_reg_gyro", return_value=0xFF):
            self.assertFalse(self.imu._check_chip_ids())

    # --- Setters: ODR and range bit masking --------------------------------

    # def test_set_accel_odr_masks_bits(self):
        # ACC_CONF: new = (current & 0x0F) | (odr<<4)
        # with mock.patch.object(self.imu, "_read_reg_accel", return_value=0xAB) as rr, \
        #      mock.patch.object(self.imu, "_write_reg_accel") as wr:
        #     run(self.imu.set_accel_odr(bmi088.AccelODR.ODR_1600HZ))  # 0x0C
        #     # expected: (0xAB & 0x0F)=0x0B; (0x0C<<4)=0xC0; => 0xCB
        #     wr.assert_called_once_with(bmi088.ACC_CONF, 0xCB)
    def test_set_gyro_odr_masks_bits(self):
        # GYR_BW: new = (current & 0xF0) | (odr & 0x0F)
        with mock.patch.object(self.imu, "_read_reg_gyro", return_value=0x3C) as rr, \
             mock.patch.object(self.imu, "_write_reg_gyro") as wr:
            run(self.imu.set_gyro_odr(bmi088.GyroODR.ODR_100HZ))  # 0x07
            # expected: (0x3C & 0xF0)=0x30; | 0x07 -> 0x37
            wr.assert_called_once_with(bmi088.GYR_BW_REG, 0x37)

    def test_set_ranges_write_registers_and_update_cache(self):
        # # with mock.patch.object(self.imu, "_write_reg_accel") as wa, \
        with mock.patch.object(self.imu, "_write_reg_gyro") as wg:
            run(self.imu.set_accel_range(bmi088.AccelRange.RANGE_24G))
            # wa.assert_called_once_with(bmi088.ACC_RANGE_REG, bmi088.AccelRange.RANGE_24G & 0x03)
            self.assertEqual(self.imu.accel_range, bmi088.AccelRange.RANGE_24G)

            run(self.imu.set_gyro_range(bmi088.GyroRange.RANGE_250DPS))
            wg.assert_called_once_with(bmi088.GYR_RANGE_REG, bmi088.GyroRange.RANGE_250DPS & 0x07)
            self.assertEqual(self.imu.gyro_range, bmi088.GyroRange.RANGE_250DPS)

    # --- Data path: scaling math --------------------------------------------

    # def test_read_accel_scaling(self):
    #     # For RANGE_6G scale = 9.807/512. If raw = (512, 0, -512),
    #     # expect (9.807, 0.0, -9.807)
    #     self.imu.accel_range = bmi088.AccelRange.RANGE_6G
    #     with mock.patch.object(self.imu, "read_accel_raw", new=mock.AsyncMock(return_value=(512, 0, -512))):
    #         ax, ay, az = run(self.imu.read_accel())
    #         self.assertAlmostEqual(ax, 9.807, places=3)
    #         self.assertAlmostEqual(ay, 0.0, places=6)
    #         self.assertAlmostEqual(az, -9.807, places=3)

    def test_read_gyro_scaling(self):
        # RANGE_1000DPS scale = 1000/32768 dps/LSB.
        # Raw (32767, 0, -32768) -> ~ (999.97 dps, 0, -1000 dps) in dps, then *deg2rad
        self.imu.gyro_range = bmi088.GyroRange.RANGE_1000DPS
        with mock.patch.object(self.imu, "read_gyro_raw", new=mock.AsyncMock(return_value=(32767, 0, -32768))):
            gx, gy, gz = run(self.imu.read_gyro())
            self.assertAlmostEqual(gx, (1000.0/32768.0*32767) * bmi088.DEG2RAD, places=5)
            self.assertAlmostEqual(gy, 0.0, places=9)
            self.assertAlmostEqual(gz, (-1000.0/32768.0*32768) * bmi088.DEG2RAD, places=5)

    def test_read_temperature_linearization(self):
        # temp = 23.0 + raw/512.0; let raw=1024 => 25.0 C
        with mock.patch.object(self.imu, "read_temperature_raw", new=mock.AsyncMock(return_value=1024)):
            t = run(self.imu.read_temperature())
            self.assertAlmostEqual(t, 25.0)

    # --- Begin sequence -----------------------------------------------------

    def test_begin_sequence_calls(self):
        # Make chip IDs OK; spy on register writes and the set_* calls
        with mock.patch.object(self.imu, "_check_chip_ids", return_value=True), \
            mock.patch.object(self.imu, "_write_reg_gyro") as wrg, \
            mock.patch.object(self.imu, "set_gyro_range", new=mock.AsyncMock()) as sgr, \
            mock.patch.object(self.imu, "set_gyro_odr", new=mock.AsyncMock()) as sgo:
            run(self.imu.begin())

            # soft_reset writes (called inside begin via soft_reset)
            # Note: soft_reset is awaited in begin, which calls both writes. We didn't patch soft_reset,
            # so assert that ACC/GYR power & mode registers were set (after soft reset)
            # Power up accel and gyro per begin()
            # wra.assert_any_call(bmi088.ACC_PWR_CONF, 0x00)
            # wra.assert_any_call(bmi088.ACC_PWR_CTRL, 0x04)
            wrg.assert_any_call(bmi088.GYR_LPM1, 0x00)

            # Default configuration setters are awaited
            sgr.assert_awaited()
            sgo.assert_awaited()

    # --- Read block/register plumbing (optional sanity check) ---------------

    def test_check_read_block_api_contract(self):
        # Ensure _read_reg_* returns first byte of block
        # with mock.patch.object(self.imu, "_read_block_accel", return_value=bytes([0xAB])):
        #     self.assertEqual(self.imu._read_reg_accel(0x10), 0xAB)
        with mock.patch.object(self.imu, "_read_block_gyro", return_value=bytes([0xCD])):
            self.assertEqual(self.imu._read_reg_gyro(0x10), 0xCD)


if __name__ == "__main__":
    unittest.main()
