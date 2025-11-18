# code.py
from drivers import bmi088 
from Adafruit_CircuitPython_asyncio import asyncio
import board, busio

async def read_gyro():
    spi = busio.SPI(board.GYRO_SCLK, MOSI=board.GYRO_MOSI, MISO=board.GYRO_MISO)
    gyro = bmi088.Bmi088Gyro(spi, cs_gyro_pin=board.GYRO_CS1)
    await gyro.begin()
    await gyro.set_gyro_range(bmi088.GyroRange.RANGE_1000DPS)
    await gyro.set_gyro_odr(bmi088.GyroODR.ODR_400HZ)

    while True:
        gx, gy, gz = await gyro.read_gyro()
        print(f"gyro [rad/s]: {gx:.3f}, {gy:.3f}, {gz:.3f}")
        await asyncio.sleep(0.05)  # 20 Hz print rate

def main() :
    print("hello world")
    asyncio.run(read_gyro())
