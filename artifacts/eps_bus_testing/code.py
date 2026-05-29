"""
Allows for enabling/disabling each of the buses on the EPS board.
"""
import digitalio
import board
import ads1118

from datastores import DsCommands

# Initialize pins

en_3v3_bus_pin = digitalio.DigitalInOut(board.EN_3V3_BUS)
en_3v3_bus_pin.direction = digitalio.Direction.OUTPUT

en_5v_bus_pin = digitalio.DigitalInOut(board.EN_5V_BUS)
en_5v_bus_pin.direction = digitalio.Direction.OUTPUT

en_12vlp_bus_pin = digitalio.DigitalInOut(board.EN_12VLP_BUS)
en_12vlp_bus_pin.direction = digitalio.Direction.OUTPUT

en_12vhp_bus_pin = digitalio.DigitalInOut(board.EN_12VHP_BUS)
en_12vhp_bus_pin.direction = digitalio.Direction.OUTPUT

print("starting adcs")

adc1 = ads1118.Ads1118(board.ADC_SCK, board.ADC_MOSI, board.ADC_MISO, board.ADC_CS1)
# adc2 = ads1118.Ads1118(board.ADC_SCK, board.ADC_MOSI, board.ADC_MISO, board.ADC_CS2)
# adc3 = ads1118.Ads1118(board.ADC_SCK, board.ADC_MOSI, board.ADC_MISO, board.ADC_CS3)
# adc4 = ads1118.Ads1118(board.ADC_SCK, board.ADC_MOSI, board.ADC_MISO, board.ADC_CS4)
# adc5 = ads1118.Ads1118(board.ADC_SCK, board.ADC_MOSI, board.ADC_MISO, board.ADC_CS5)
# adc6 = ads1118.Ads1118(board.ADC_SCK, board.ADC_MOSI, board.ADC_MISO, board.ADC_CS6)
# adc7 = ads1118.Ads1118(board.ADC_SCK, board.ADC_MOSI, board.ADC_MISO, board.ADC_CS7)

print("working")

def set_3v3(eps_ds_commands: DsCommands, enable: bool):
    """Enables or disables 3v3 bus and sets corresponding value in DsCommands"""
    en_3v3_bus_pin.value = enable
    eps_ds_commands.bus_3v3_enabled = enable


def set_5v(eps_ds_commands: DsCommands, enable: bool):
    """Enables or disables 5v bus and sets corresponding value in DsCommands"""
    en_5v_bus_pin.value = enable
    eps_ds_commands.bus_5v_enabled = enable


def set_12vlp(eps_ds_commands: DsCommands, enable: bool):
    """Enables or disables 12vlp bus and sets corresponding value in DsCommands"""
    en_12vlp_bus_pin.value = enable
    eps_ds_commands.bus_12vlp_enabled = enable


def set_12vhp(eps_ds_commands: DsCommands, enable: bool):
    """Enables or disables 12vhp bus and sets corresponding value in DsCommands"""
    en_12vhp_bus_pin.value = enable
    eps_ds_commands.bus_12vhp_enabled = enable

def read_5v():
    """Prints the value of the 5v bus"""
    print(adc1.take_sample(3))

def test_buses():
    """Reads commands from the user to enable and disable buses"""
    print("=" * 100)
    print(f'{"=" * 40}  EPS Bus Testing  {"=" * 41}')
    print("=" * 100)

    ds_commands = DsCommands()

    while True:
        print()
        command = input(
            "Enter a command to control a bus (syntax: [enable/disable] [3v3, 5v, 12vlp, 12vhp]), or print a value (syntax: [V/I] 3v3in/3v3out/...):"
        )

        split = command.split()

        if len(split) != 2:
            print(
                f"Invalid syntax. There should be 2 arguments separated by a space but you input {split.__len__}."
            )
            continue

        if split[0] == "enable":
            enable_val = True
        elif split[0] == "disable":
            enable_val = False
        else:
            print(
                f'Invalid syntax. The argument "{split[0]}" must be either "enable" or "disable".'
            )
            continue

        if split[1] == "3v3":
            set_3v3(ds_commands, enable_val)
        elif split[1] == "5v":
            set_5v(ds_commands, enable_val)
        elif split[1] == "12vlp":
            set_12vlp(ds_commands, enable_val)
        elif split[1] == "12vhp":
            set_12vhp(ds_commands, enable_val)
        elif split[0] == "V" and split[1] == "5Vout":
            read_5v()
        else:
            print(
                f'Invalid syntax. The argument "{split[1]}" must be either "3v3", "5v", "12vlp", or "12vhp".'
            )

if __name__ == "__main__":
    test_buses()
