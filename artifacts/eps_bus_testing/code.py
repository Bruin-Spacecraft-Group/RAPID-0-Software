"""
Allows for enabling/disabling each of the buses on the EPS board.
"""

from datastores.eps import DsCommands
import board
import digitalio

if __name__ == "__main__":
    print("=" * 100)
    print(f'{"=" * 40}  EPS Bus Testing  {"=" * 41}')
    print("=" * 100)

    ds_commands = DsCommands()

    while True:
        print()
        command = input(
            "Enter a command to control a bus (syntax: [enable/disable] [3v, 5v, 12vlp, 12vhp]):"
        )

        split = command.split()

        if split.__len__ != 2:
            print(
                f"Invalid syntax. There should be 2 arguments separated by a space but you input {split.__len__}."
            )
            continue

        if split[0] == "enable":
            enable = True
        elif split[0] == "disable":
            enable = False
        else:
            print(
                f'Invalid syntax. The argument "{split[0]}" must be either "enable" or "disable".'
            )
            continue

        if split[1] == "3v3":
            set_3v3(ds_commands, enable)
        elif split[1] == "5v":
            set_5v(ds_commands, enable)
        elif split[1] == "12vlp":
            set_12vlp(ds_commands, enable)
        elif split[1] == "12vhp":
            set_12vhp(ds_commands, enable)
        else:
            print(
                f'Invalid syntax. The argument "{split[1]}" must be either "3v3", "5v", "12vlp", or "12vhp".'
            )




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
