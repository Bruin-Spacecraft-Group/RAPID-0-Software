# code.py
from drivers import bmi088 
import asyncio
import board, busio

import microcontroller

#IMU (BMI088) Bus Pins
GYRO_SCLK = microcontroller.pin.PA05
GYRO_MOSI = microcontroller.pin.PA07
GYRO_MISO = microcontroller.pin.PA06
GYRO_CS1 = microcontroller.pin.PA10
GYRO_CS2 = microcontroller.pin.PA11
GYRO_CS3 = microcontroller.pin.PA12

async def read_gyro():
    spi = busio.SPI(GYRO_SCLK, MOSI=GYRO_MOSI, MISO=GYRO_MISO)
    gyro = bmi088.Bmi088Gyro(spi, cs_gyro_pin=GYRO_CS3)
    await gyro.begin()
    await gyro.set_gyro_range(bmi088.GyroRange.RANGE_1000DPS)
    await gyro.set_gyro_odr(bmi088.GyroODR.ODR_400HZ)

    while True:
        gx, gy, gz = await gyro.read_gyro()
        print(f"gyro [rad/s]: {gx:.3f}, {gy:.3f}, {gz:.3f}")
        await asyncio.sleep(0.05)  # 20 Hz print rate

if __name__ == "__main__":
    print("is running2...")
    asyncio.run(read_gyro())
