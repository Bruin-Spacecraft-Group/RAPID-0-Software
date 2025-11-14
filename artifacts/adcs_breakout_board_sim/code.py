# code.py
from bmi088 import Bmi088Gyro, GyroRange, GyroODR
import asyncio, board, busio

async def main():
    spi = busio.SPI(board.SCLK, MOSI=board.MOSI, MISO=board.MISO)
    gyro = Bmi088Gyro(spi, cs_gyro_pin=board.GYRO_CS1)
    await gyro.begin()
    await gyro.set_gyro_range(GyroRange.RANGE_1000DPS)
    await gyro.set_gyro_odr(GyroODR.ODR_400HZ)

    while True:
        gx, gy, gz = await gyro.read_gyro()
        print(f"gyro [rad/s]: {gx:.3f}, {gy:.3f}, {gz:.3f}")
        await asyncio.sleep(0.05)  # 20 Hz print rate

asyncio.run(main())
