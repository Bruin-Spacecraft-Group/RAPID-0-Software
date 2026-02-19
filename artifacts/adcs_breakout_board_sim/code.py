from drivers import bmi088
import asyncio
import busio
import microcontroller


async def run_fixed_setting():
    spi = busio.SPI(
        microcontroller.pin.PA05,
        MOSI=microcontroller.pin.PA07,
        MISO=microcontroller.pin.PA06,
    )

    gyro = bmi088.Bmi088Gyro(
        spi,
        cs_gyro_pin_or_dio=microcontroller.pin.PE10,  # CS3
        baudrate=1600,
        polarity=1,
        phase=1,
        read_dummy_bytes=2,
        cs_active_low=True,
    )

    await gyro.begin(verify_chip_id=False)
    print("fixed setting: CS3 mode=(0,0) dummy=2 baud=1600 cs_active_low=True")

    # Repeat self-test a few times to check consistency.
    for i in range(2):
        st = await gyro.self_test_gyro(wait_s=0, timeout_s=20)
        print(
            "self_test",
            i,
            "raw=0x{:02X}".format(st["raw_0x3C"]),
            "b1={}".format(st["bit1"]),
            "b2={}".format(st["bit2"]),
            "b3={}".format(st["bit4"]),
            "timeout={}".format(st["timed_out"]),
        )
        await asyncio.sleep(0.05)

    # Stream gyro values.
    for _ in range(1000):
        gx_raw, gy_raw, gz_raw = await gyro.read_gyro_raw()
        gx, gy, gz = await gyro.read_gyro()
        print(
            "gyro_raw:",
            gx_raw,
            gy_raw,
            gz_raw,
            "gyro_rad_s:",
            "{:.3f}".format(gx),
            "{:.3f}".format(gy),
            "{:.3f}".format(gz),
        )
        await asyncio.sleep(0.05)

    print("FIXED_TEST_DONE")


if __name__ == "__main__":
    print("is running...")
    asyncio.run(run_fixed_setting())
