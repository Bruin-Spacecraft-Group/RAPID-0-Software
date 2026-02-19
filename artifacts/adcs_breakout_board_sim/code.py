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
        cs_gyro_pin_or_dio=microcontroller.pin.PE11,  # CS3
        baudrate=1600,
        polarity=1,
        phase=1,
        read_dummy_bytes=2,
        cs_active_low=True,
    )

    await gyro.begin(verify_chip_id=False)
    print("fixed setting: CS2 mode=(1,1) dummy=2 baud=1600 cs_active_low=True")

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

    # Stream gyro data bytes (0x02..0x07) with no conversion.
    for _ in range(1000):
        data = gyro._read_block_gyro(bmi088.GYR_DATA_START, 6)
        print(
            "gyro_bytes:",
            "b0=0x{:02X}".format(data[0]),
            "b1=0x{:02X}".format(data[1]),
            "b2=0x{:02X}".format(data[2]),
            "b3=0x{:02X}".format(data[3]),
            "b4=0x{:02X}".format(data[4]),
            "b5=0x{:02X}".format(data[5]),
        )
        await asyncio.sleep(0.05)

    print("FIXED_TEST_DONE")


if __name__ == "__main__":
    print("is running...")
    asyncio.run(run_fixed_setting())
