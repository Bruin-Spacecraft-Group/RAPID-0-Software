"""
Allows for enabling/disabling each of the buses on the EPS board.
"""

from datastores.eps import DsCommands
import board

if __name__ == "__main__":
    pass


def set_3v3(eps_ds_commands: DsCommands, enable: bool):
    pass


def set_5v(eps_ds_commands: DsCommands, enable: bool):
    pass


def set_12vlp(eps_ds_commands: DsCommands, enable: bool):
    pass


def set_12vhp(eps_ds_commands: DsCommands, enable: bool):
    pass
