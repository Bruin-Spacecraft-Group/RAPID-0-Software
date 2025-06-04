"""
Pin definitions of the CDH engineering model board.

The variables defined in this file should be used when working with the corresponding pins
instead of the previous approach of importing the CircuitPython defined 'board' and
'microcontroller' module(s). This ensures any future changes to the board can be
easily integrated into the existing codebase.
"""

import microcontroller


# Pins which connect to the camera
CAM_HEAT_N = microcontroller.pin.PB07
CAM_SCL = microcontroller.pin.PB08
CAM_SDA = microcontroller.pin.PB09
CAM_SCK = microcontroller.pin.PE02
CAM_CS = microcontroller.pin.PE03
CAM_MISO = microcontroller.pin.PE05
CAM_MOSI = microcontroller.pin.PE06


# RS485 pins for inter-subsystem communication
RS485_1_RX = microcontroller.pin.PE07
RS485_1_TX = microcontroller.pin.PE08
RS485_1_DE = microcontroller.pin.PE09

RS485_2_RX = microcontroller.pin.PB12
RS485_2_TX = microcontroller.pin.PB13
RS485_2_DE = microcontroller.pin.PB14

RS485_3_RX = microcontroller.pin.PE00
RS485_3_TX = microcontroller.pin.PE01
RS485_3_DE = microcontroller.pin.PD15


# Watchdog pin
WDI = microcontroller.pin.PC13


# Battery Pack Heater Pins
BAT_HEAT1N = microcontroller.pin.PA01
BAT_HEAT2N = microcontroller.pin.PA00

# USB Communication Pins
USB_ID = microcontroller.pin.PA10
USB_N = microcontroller.pin.PA11
USB_P = microcontroller.pin.PA12