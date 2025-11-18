"""
Pin definitions for the board which runs the adcs_breakout_board_sim artifact.
"""

import microcontroller

#IMU (BMI088) Bus Pins
GYRO_SCLK = microcontroller.pin.PA05
GYRO_MOSI = microcontroller.pin.PA07
GYRO_MISO = microcontroller.pin.PA06
GYRO_CS1 = microcontroller.pin.PA10
GYRO_CS2 = microcontroller.pin.PA11
GYRO_CS3 = microcontroller.pin.PA12
