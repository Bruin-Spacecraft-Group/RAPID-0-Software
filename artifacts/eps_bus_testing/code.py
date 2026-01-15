"""
Allows for enabling/disabling each of the buses on the EPS board.
"""

from datastores.eps import DsCommands
import board
import digitalio

if __name__ == "__main__":
    pass




def set_3v3(eps_ds_commands: DsCommands, enable: bool):
    en_3v3_bus_pin = digitalio.DigitalInOut(board.EN_3V3_BUS)
    en_3v3_bus_pin.direction = digitalio.Direction.OUTPUT
    en_3v3_bus_pin.value = enable
    eps_ds_commands.bus_3v3_enabled = enable


def set_5v(eps_ds_commands: DsCommands, enable: bool):
    en_5v_bus_pin = digitalio.DigitalInOut(board.EN_5V_BUS)
    en_5v_bus_pin.direction = digitalio.Direction.OUTPUT
    en_5v_bus_pin.value = enable
    eps_ds_commands.bus_5v_enabled = enable



def set_12vlp(eps_ds_commands: DsCommands, enable: bool):
    en_12vlp_bus_pin = digitalio.DigitalInOut(board.EN_12VLP_BUS)
    en_12vlp_bus_pin.direction = digitalio.Direction.OUTPUT
    en_12vlp_bus_pin.value = enable
    eps_ds_commands.bus_12vlp_enabled = enable


def set_12vhp(eps_ds_commands: DsCommands, enable: bool):
    en_12vhp_bus_pin = digitalio.DigitalInOut(board.EN_12VHP_BUS)
    en_12vhp_bus_pin.direction = digitalio.Direction.OUTPUT
    en_12vhp_bus_pin.value = enable
    eps_ds_commands.bus_12vhp_enabled = enable
