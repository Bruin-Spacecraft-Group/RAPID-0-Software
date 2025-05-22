"""
Pin definitions of the CDH engineering model board.

The variables defined in this file should be used when working with the corresponding pins
instead of the previous approach of importing the CircuitPython defined 'board' and
'microcontroller' module(s). This ensures any future changes to the board can be
easily integrated into the existing codebase.
"""

import microcontroller


# Pins which connect to the camera
CAM_HEAT_N = microcontroller.pin.PB7
CAM_SCL = microcontroller.pin.PB8
CAM_SDA = microcontroller.pin.PB9
CAM_SCK = microcontroller.pin.PE2
CAM_CS = microcontroller.pin.PE3
CAM_MISO = microcontroller.pin.PE5
CAM_MOSI = microcontroller.pin.PE6


# RS485 pins for inter-subsystem communication
RS485_1_RX = microcontroller.pin.PE7
RS485_1_TX = microcontroller.pin.PE8
RS485_1_DE = microcontroller.pin.PE9

RS485_2_RX = microcontroller.pin.PB12
RS485_2_TX = microcontroller.pin.PB13
RS485_2_DE = microcontroller.pin.PB14

RS485_3_RX = microcontroller.pin.PE0
RS485_3_TX = microcontroller.pin.PE1
RS485_3_DE = microcontroller.pin.PD15


# Watchdog pin
WDI = microcontroller.pin.PC13