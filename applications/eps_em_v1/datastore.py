"""
Module of objects and classes which store data pertaining to the current state of the
EPS system for all tasks to update and use. Readings that have not yet been initialized
are set to `None` throughout this module.
"""


class Datastore:
    """
    A top-level datastore object. An object of this type contains all state data for an
    EPS system either directly or indirectly.
    """

    def __init__(self):
        self.batteries: DsBatteryPack = DsBatteryPack()
        self.bus_3v3: DsOutputBus = DsOutputBus()
        self.bus_5v: DsOutputBus = DsOutputBus()
        self.bus_12vlp: DsOutputBus = DsOutputBus()
        self.bus_12vhp: DsOutputBus = DsOutputBus()
        self.mppt: DsMppt = DsMppt()
        self.solar_array: DsSolarArray = DsSolarArray()
        self.control_commands: DsCommands = DsCommands()


class DsBatteryPack:
    """
    A datastore object representing state data for a battery pack. Includes 3 strings of
    cells each in a 2S configuration, four temperature data points, and summary statistics
    of pack electrical state.
    """

    def __init__(self):
        self.string_1: DsBatteryString = DsBatteryString()
        self.string_2: DsBatteryString = DsBatteryString()
        self.string_3: DsBatteryString = DsBatteryString()
        self.temperatures: list[float] = [None] * 4
        self.pack_capacity_mah: float = None
        self.filled_capacity_mah: float = None


class DsOutputBus:
    """
    A datastore object representing state data for an switched-mode power supply which takes
    power from the battery pack and produces a regulated voltage. Includes input and output
    currents, whether or not the supply is enabled, and the actual measured output voltage
    for monitoring.
    """

    def __init__(self):
        self.input_current: float = None
        self.output_current: float = None
        self.output_voltage: float = None
        self.enabled: bool = None


class DsMppt:
    """
    A datastore object representing state data for a maximum power point tracker. Includes input
    and output currents, the measured input voltage, and control mode information from the mppt.
    """

    def __init__(self):
        self.input_current: float = None
        self.output_current: float = None
        self.input_voltage: float = None
        self.enabled: bool = None
        self.low_power_mode: bool = None
        self.charging_stage: int = None
        self.fault: str = None


class DsSolarArray:
    """
    A datastore object representing state data for a solar array. Includes 4 independent panels.
    """

    def __init__(self):
        self.panels: list[DsSolarPanel] = [DsSolarPanel() for i in range(4)]


class DsBatteryString:
    """
    A datastore object representing state data for a single 2S battery string. Includes cell voltage
    and current values. Also includes protection and balancing control information.
    """

    def __init__(self):
        self.top_cell_voltage: float = None
        self.bottom_cell_voltage: float = None
        self.output_current: float = None
        self.discharging_enabled: bool = None
        self.charging_enabled: bool = None
        self.top_balancing_shunt_enabled: bool = None
        self.bottom_balancing_shunt_enabled: bool = None


class DsSolarPanel:
    """
    A datastore object representing state data for a single solar panel. Includes temperature and
    output current measurements.
    """

    def __init__(self):
        self.top_temperature: float = None
        self.middle_temperature: float = None
        self.bottom_temperature: float = None
        self.output_current: float = None


class DsCommands:
    """
    A datastore object containing the latest set of operational constraints that have been dictated
    through system control commands from CDH.
    """

    def __init__(self):
        pass
