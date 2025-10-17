"""
Defines wiring that goes to the EPS microcontroller on the EPS flatsat PCB from June 2024.

Software should refer to the pins named here rather than any pin definitions in the `board`
or `microcontroller` modules so that future PCB changes, as needed, don't necessitate
widespread changes to existing, tested control software modules. Using these definitions
also promotes code readability.
"""

import microcontroller

BOARD_ID = "rapid_0"

# power supply control pins
EN_3V3_BUS = microcontroller.pin.PA14
EN_5V_BUS = microcontroller.pin.PA15
EN_12VLP_BUS = microcontroller.pin.PD03
EN_12VHP_BUS = microcontroller.pin.PD00
MPPT_EN = microcontroller.pin.PD01
MPPT_STATUS = microcontroller.pin.PD02

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

# battery pack balancing controls
S1_TOP_BALANCE = microcontroller.pin.PB00
S1_BOTTOM_BALANCE = microcontroller.pin.PB01
S2_TOP_BALANCE = microcontroller.pin.PE07
S2_BOTTOM_BALANCE = microcontroller.pin.PE09
S3_TOP_BALANCE = microcontroller.pin.PE12
S3_BOTTOM_BALANCE = microcontroller.pin.PE10

# battery pack protection controls
S1_DISCHARGE_SHD = microcontroller.pin.PC04
S1_CHARGE_SHD = microcontroller.pin.PE13
S2_DISCHARGE_SHD = microcontroller.pin.PB02
S2_CHARGE_SHD = microcontroller.pin.PC05
S3_DISCHARGE_SHD = microcontroller.pin.PE11
S3_CHARGE_SHD = microcontroller.pin.PE08

# inter-subsystem RS485 bus
RS485_1_TX = microcontroller.pin.PD05
RS485_1_RX = microcontroller.pin.PD06
RS485_1_DE = microcontroller.pin.PD04
RS485_2_TX = microcontroller.pin.PD08
RS485_2_RX = microcontroller.pin.PD09
RS485_2_DE = microcontroller.pin.PD12

# other
WATCHDOG_FEED = microcontroller.pin.PA00
