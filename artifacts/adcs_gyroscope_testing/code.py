from drivers import bmi088
import asyncio
import busio
import time
import microcontroller
from drivers import reaction_wheel

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

rw = reaction_wheel.ReactionWheel(
    microcontroller.pin.PA00, microcontroller.pin.PA01, microcontroller.pin.PA04
)


def _to_int16(msb, lsb):
    value = (msb << 8) | lsb
    if value & 0x8000:
        value -= 0x10000
    return value


async def run_fixed_read():
    await gyro.begin(verify_chip_id=False)
    print("fixed: CS1 mode=(0,0) dummy=0 baud=1600 cs_active_low=True")

    st = await gyro.self_test_gyro(wait_s=0.05, timeout_s=0.8)
    raw = st["raw_0x3C"]
    file.write(
        "self_test",
        "raw=0x{:02X}".format(raw),
        "bits={:08b}".format(raw),
        "b1={}".format(st["bit1"]),
        "b2={}".format(st["bit2"]),
        "b3={}".format(st["bit4"]),
        "timeout={}".format(st["timed_out"]),
        "-----------------",
    )
    file.flush()
    await asyncio.sleep(0.05)

    time_diff = 0
    start_time = time.monotonic_ns
    while time_diff < 1000000:
        data = gyro._read_block_gyro(bmi088.GYR_DATA_START, 6)
        # Convert from the same byte sample printed above.
        gx = _to_int16(data[1], data[0])
        gy = _to_int16(data[3], data[2])
        gz = _to_int16(data[5], data[4])
        file.write(
            "sample",
            "bytes=",
            " ".join("0x{:02X}".format(b) for b in data),
            "raw_xyz=({}, {}, {})".format(gx, gy, gz),
            "----------------------",
        )
        file.flush()
        end_time = time.monotonic_ns
        time_diff = abs(end_time - start_time)
        # await asyncio.sleep(0.05)

    file.close()
    print("DONE")


# reaction wheel code
async def spin_input_speed():
    while True:
        pc = input("Speed 0-100: ")
        dc = pc / 100 * (2**16 - 1)
        rw.set_speed(dc)


if __name__ == "__main__":
    print("is running...")
    asyncio.run(run_fixed_read())
    asyncio.run(spin_input_speed())
