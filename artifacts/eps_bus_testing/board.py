"""
Pin definitions for the nucleo board which runs the eps_bus_testing artifact.
"""

import microcontroller

EN_3V3_BUS = microcontroller.pin.PA14
EN_5V_BUS = microcontroller.pin.PA15
EN_12VLP_BUS = microcontroller.pin.PD03
EN_12VHP_BUS = microcontroller.pin.PD00

# SPI to ADS1118 ADCs on the board and the solar array
ADC_SCK = microcontroller.pin.PA05
ADC_MOSI = microcontroller.pin.PA07
ADC_MISO = microcontroller.pin.PA06
ADC_CS1 = microcontroller.pin.PA13
ADC_CS2 = microcontroller.pin.PA09
ADC_CS3 = microcontroller.pin.PA08
ADC_CS4 = microcontroller.pin.PA04
ADC_CS5 = microcontroller.pin.PA03
ADC_CS6 = microcontroller.pin.PA02
ADC_CS7 = microcontroller.pin.PA01
SA_ADC_CS1 = microcontroller.pin.PE02
SA_ADC_CS2 = microcontroller.pin.PE03
SA_ADC_CS3 = microcontroller.pin.PE05
SA_ADC_CS4 = microcontroller.pin.PE04
