"""
Allows for enabling/disabling each of the buses on the EPS board.
"""

from datastores.eps import DsCommands
import board
import digitalio

if __name__ == "__main__":
    pass


def set_3v3(eps_ds_commands: DsCommands, enable: bool):
    pass


def set_5v(eps_ds_commands: DsCommands, enable: bool):
    pass


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
