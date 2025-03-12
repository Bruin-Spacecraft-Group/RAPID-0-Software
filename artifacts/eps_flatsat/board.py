"""
Pin definitions for the board which runs the eps_flatsat artifact.
Defines wiring that goes to the EPS microcontroller on the EPS flatsat PCB from June 2024.

Software should refer to the pins named here rather than any pin definitions in the `board`
or `microcontroller` modules so that future PCB changes, as needed, don't necessitate
widespread changes to existing, tested control software modules. Using these definitions
also promotes code readability.
"""

import microcontroller

# power supply control pins
EN_3V3_BUS = microcontroller.pin.PA12
EN_5V_BUS = microcontroller.pin.PA13
EN_12VLP_BUS = microcontroller.pin.PA14
EN_12VHP_BUS = microcontroller.pin.PA15

# SPI to ADS1118 ADCs on the board and the solar array
ADC_SCK = microcontroller.pin.PA17
ADC_MOSI = microcontroller.pin.PA16
ADC_MISO = microcontroller.pin.PA19
ADC_CS1 = microcontroller.pin.PA18
ADC_CS2 = microcontroller.pin.PA23
ADC_CS3 = microcontroller.pin.PA22
ADC_CS4 = microcontroller.pin.PB23
ADC_CS5 = microcontroller.pin.PB22
ADC_CS6 = microcontroller.pin.PA27
ADC_XCS1 = microcontroller.pin.PA00
ADC_XCS2 = microcontroller.pin.PA01
ADC_XCS3 = microcontroller.pin.PA02
ADC_XCS4 = microcontroller.pin.PB04

# battery pack balancing controls
# (BMS not populated on flatsat PCB)

# battery pack protection controls
# (BMS not populated on flatsat PCB)

# inter-subsystem SPI bus
BUS_SCK = microcontroller.pin.PB17
BUS_MOSI = microcontroller.pin.PA21
BUS_MISO = microcontroller.pin.PB16
EPS_CS = microcontroller.pin.PA20
