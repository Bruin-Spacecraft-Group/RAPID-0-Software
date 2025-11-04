import unittest
import bmi088


class BMI088_Test(unittest.TestCase):

    _NON_INT_OBJECTS = [object(), {}, [], 3.14, -1.5, "a"]

    def test_accel_range_validation(self):
        valid_ranges = [
            bmi088.AccelRange.RANGE_3G,
            bmi088.AccelRange.RANGE_6G,
            bmi088.AccelRange.RANGE_12G,
            bmi088.AccelRange.RANGE_24G,
        ]
        for r in valid_ranges:
            self.assertIn(r, bmi088.ACC_SCALE.keys())

        for bad in self._NON_INT_OBJECTS:
            with self.assertRaises((TypeError, KeyError, AssertionError)):
                _ = bmi088.ACC_SCALE[bad]

        with self.assertRaises(KeyError):
            _ = bmi088.ACC_SCALE[99]

    def test_gyro_range_validation(self):
        valid_ranges = [
            bmi088.GyroRange.RANGE_2000DPS,
            bmi088.GyroRange.RANGE_1000DPS,
            bmi088.GyroRange.RANGE_500DPS,
            bmi088.GyroRange.RANGE_250DPS,
            bmi088.GyroRange.RANGE_125DPS,
        ]
        for r in valid_ranges:
            self.assertIn(r, bmi088.GYRO_SCALE.keys())

        for bad in self._NON_INT_OBJECTS:
            with self.assertRaises((TypeError, KeyError, AssertionError)):
                _ = bmi088.GYRO_SCALE[bad]

        with self.assertRaises(KeyError):
            _ = bmi088.GYRO_SCALE[99]

    def test_int16_conversion(self):
        # Positive number
        self.assertEqual(bmi088.Bmi088._to_int16(0x12, 0x34), 0x1234)
        # Negative number
        self.assertEqual(bmi088.Bmi088._to_int16(0xFF, 0x00), -256)
        self.assertEqual(bmi088.Bmi088._to_int16(0x80, 0x00), -32768)
        self.assertEqual(bmi088.Bmi088._to_int16(0x7F, 0xFF), 32767)

    def test_accel_scaling_values(self):
        # Verify conversion constants are physically meaningful
        for k, v in bmi088.ACC_SCALE.items():
            self.assertTrue(0 < v < 0.2, f"Invalid scale {v} for range {k}")

    def test_gyro_scaling_values(self):
        for k, v in bmi088.GYRO_SCALE.items():
            self.assertTrue(0 < v < 0.1, f"Invalid gyro scale {v} for range {k}")

    def test_temperature_conversion_formula(self):
        # BMI088 datasheet: Temp = 23 + raw / 512
        raw_values = [0, 512, -512, 1024]
        expected = [23.0, 24.0, 22.0, 25.0]
        for raw, exp in zip(raw_values, expected):
            # Manually pack raw into two bytes big-endian
            if raw < 0:
                raw &= 0xFFFF
            msb, lsb = (raw >> 8) & 0xFF, raw & 0xFF
            val = bmi088.Bmi088._to_int16(msb, lsb)
            temp_c = 23.0 + val / 512.0
            self.assertAlmostEqual(temp_c, exp, places=3)

    def test_combined_read_data_structure(self):
        """Test that read_all() returns the expected keys."""
        imu = bmi088.Bmi088(spi_bus=None, cs_accel=None, cs_gyro=None)
        # monkeypatch async methods to avoid hardware
        async def fake_accel(): return (1.0, 2.0, 3.0)
        async def fake_gyro(): return (0.1, 0.2, 0.3)
        async def fake_temp(): return 25.0
        imu.read_accel = fake_accel
        imu.read_gyro = fake_gyro
        imu.read_temperature = fake_temp

        import asyncio
        result = asyncio.run(imu.read_all())
        self.assertIn("accel_mss", result)
        self.assertIn("gyro_rads", result)
        self.assertIn("temp_C", result)
        self.assertEqual(result["temp_C"], 25.0)
        self.assertAlmostEqual(result["gyro_rads"][1], 0.2, places=2)


if __name__ == "__main__":
    unittest.main()