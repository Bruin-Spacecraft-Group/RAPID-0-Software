"""
Module to implement the EPS ICD.

Part of the EPS ICD is intersubsystem communication over RS485 between CDH and EPS. This module
implements responses to requests for data that are received over the bus. It also stores
information that causes the subsystem control to comply with operation contraints sent from CDH.

An additional part of the EPS ICD is the startup timing of the output buses and the current limits
enforced on those output buses during satellite operation. This module also uses the current known
information about bus operation and mission state to enable and disable output buses as appropriate.
"""

import asyncio
import time
import digitalio

from pin_manager import PinManager
import pinout
from datastore import Datastore


async def intersubsystem_communication_task(datastore: Datastore):
    """
    Task to communicate with CDH.

    Appropriately loads all buffers to be received by CDH and sent in return at the appropriate
    times. Controls inter-subsystem communication hardware in accordance with the protocol's
    specification. Transmitted data is pulled from the `datastore` and received commands are
    placed into the `datastore`.
    """
    while True:
        print(datastore)
        await asyncio.sleep(0)


async def output_bus_control_task(datastore: Datastore):
    """
    Task which controls output buses to the rest of the satellite.

    Uses the most recent data in the `datastore` as inputs. Controls enable pins for the 3V3,
    5V, 12VLP, and 12VHP power supplies. Manages startup sequence, overcurrent conditions,
    and any relevant commands from CDH that should activate or deactivate a particular bus.
    """
    pm = PinManager.get_instance()
    m_en_3v3 = pm.create_digital_in_out(pinout.EN_3V3_BUS)
    m_en_5v = pm.create_digital_in_out(pinout.EN_5V_BUS)
    m_en_12vlp = pm.create_digital_in_out(pinout.EN_12VLP_BUS)
    m_en_12vhp = pm.create_digital_in_out(pinout.EN_12VHP_BUS)
    with m_en_3v3 as en_3v3, m_en_5v as en_5v, m_en_12vlp as en_12vlp, m_en_12vhp as en_12vhp:
        en_3v3.direction = digitalio.Direction.OUTPUT
        en_5v.direction = digitalio.Direction.OUTPUT
        en_12vlp.direction = digitalio.Direction.OUTPUT
        en_12vhp.direction = digitalio.Direction.OUTPUT
        start_time_ns = time.monotonic_ns()
        while True:
            en_3v3.value = (time.monotonic_ns() - start_time_ns) > 5 * 1e9
            en_5v.value = (time.monotonic_ns() - start_time_ns) > 10 * 1e9
            en_12vlp.value = (time.monotonic_ns() - start_time_ns) > 15 * 1e9
            en_12vhp.value = (time.monotonic_ns() - start_time_ns) > 25 * 1e9
            datastore.bus_3v3.enabled = en_3v3.value
            datastore.bus_5v.enabled = en_5v.value
            datastore.bus_12vlp.enabled = en_12vlp.value
            datastore.bus_12vhp.enabled = en_12vhp.value
            await asyncio.sleep(0)
