from drivers import bmi088_stripped
from drivers import reaction_wheel
import busio
import microcontroller as mc

spi = busio.SPI(
    mc.pin.PA05,
    MOSI=mc.pin.PA07,
    MISO=mc.pin.PA06,
)

gyro = bmi088_stripped.Bmi088Gyroscope(
    spi,
    # mc.pin.PE10,  # CS1
    mc.pin.PE12,
)

rw = reaction_wheel.ReactionWheel(
    mc.pin.PA00, mc.pin.PA01, mc.pin.PA04
)

if __name__ == "__main__":
    while True:
        input("test? ")
        print(gyro.test_chip_id())
