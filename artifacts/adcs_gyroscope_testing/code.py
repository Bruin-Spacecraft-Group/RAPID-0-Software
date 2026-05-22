from drivers import bmi088
import asyncio
import busio
import microcontroller


def _to_int16(msb, lsb):
    value = (msb << 8) | lsb
    if value & 0x8000:
        value -= 0x10000
    return value


async def run_fixed_read():
    spi = busio.SPI(
        microcontroller.pin.PA05,
        MOSI=microcontroller.pin.PA07,
        MISO=microcontroller.pin.PA06,
    )

    gyro = bmi088.Bmi088Gyro(
        spi,
        cs_gyro_pin_or_dio=microcontroller.pin.PE10,  # CS1
        baudrate=1600,
        polarity=0,
        phase=0,
        read_dummy_bytes=0,
        cs_active_low=True,
    )

    await gyro.begin(verify_chip_id=False)
    print("fixed: CS1 mode=(0,0) dummy=0 baud=1600 cs_active_low=True")

    for i in range(5):
        st = await gyro.self_test_gyro(wait_s=0.05, timeout_s=0.8)
        raw = st["raw_0x3C"]
        print(
            "self_test",
            i,
            "raw=0x{:02X}".format(raw),
            "bits={:08b}".format(raw),
            "b1={}".format(st["bit1"]),
            "b2={}".format(st["bit2"]),
            "b3={}".format(st["bit4"]),
            "timeout={}".format(st["timed_out"]),
        )
        await asyncio.sleep(0.05)

    while True:
        data = gyro._read_block_gyro(bmi088.GYR_DATA_START, 6)
        # Convert from the same byte sample printed above.
        gx = _to_int16(data[1], data[0])
        gy = _to_int16(data[3], data[2])
        gz = _to_int16(data[5], data[4])
        print(
            "sample",
            i,
            "bytes=",
            " ".join("0x{:02X}".format(b) for b in data),
            "raw_xyz=({}, {}, {})".format(gx, gy, gz),
        )
        #await asyncio.sleep(0.05)

    print("DONE")


if __name__ == "__main__":
    print("is running...")
    asyncio.run(run_fixed_read())
