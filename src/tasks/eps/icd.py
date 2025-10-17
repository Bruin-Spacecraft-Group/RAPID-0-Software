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
import board
from datastore.eps import Datastore


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

    See ICD at https://docs.google.com/document/d/1HDuXOEv7kC0Kjawf4W1BYVr5GzJt19YBkcu_MvHa1mw
    """
    pm = PinManager.get_instance()
    m_en_3v3 = pm.create_digital_in_out(board.EN_3V3_BUS)
    m_en_5v = pm.create_digital_in_out(board.EN_5V_BUS)
    m_en_12vlp = pm.create_digital_in_out(board.EN_12VLP_BUS)
    m_en_12vhp = pm.create_digital_in_out(board.EN_12VHP_BUS)
    with m_en_3v3 as en_3v3, m_en_5v as en_5v, m_en_12vlp as en_12vlp, m_en_12vhp as en_12vhp:
        en_3v3.direction = digitalio.Direction.OUTPUT
        en_5v.direction = digitalio.Direction.OUTPUT
        en_12vlp.direction = digitalio.Direction.OUTPUT
        en_12vhp.direction = digitalio.Direction.OUTPUT
        while True:
            datastore.bus_3v3.enabled = _control_tick_3v3_bus(datastore)
            datastore.bus_5v.enabled = _control_tick_5v_bus(datastore)
            datastore.bus_12vlp.enabled = _control_tick_12vlp_bus(datastore)
            datastore.bus_12vhp.enabled = _control_tick_12vhp_bus(datastore)
            en_3v3.value = datastore.bus_3v3.enabled
            en_5v.value = datastore.bus_5v.enabled
            en_12vlp.value = datastore.bus_12vlp.enabled
            en_12vhp.value = datastore.bus_12vhp.enabled
            await asyncio.sleep(0.1)


_control_tick_3v3_bus_data = {
    "tick_count": 0,
    "output_currents": [0] * 200,
}

def avg(x):
    return sum(x) / len(x)

def circ_recent (arr, count, stop):
        if stop < count:
            arr[stop - count :] + arr[:stop]
        else:
            arr[stop - count : stop]


def _control_tick_3v3_bus(datastore: Datastore):
    circ_recent = avg(arr), count, stop: (
        (arr[stop - count :] + arr[:stop])
        if stop < count
        else (arr[stop - count : stop])
    )
    avg_output_current_20s = avg(_control_tick_3v3_bus_data["output_currents"])
    if avg_output_current_20s > 0.5 * 4 / 3:
        return False
    battery_soc = (
        datastore.batteries.filled_capacity_mah / datastore.batteries.pack_capacity_mah
    )
    if battery_soc < 0.01:
        return False
    if battery_soc < 0.1 and avg_output_current_20s < 0.1 * 4 / 3:
        return False
    if _control_tick_3v3_bus_data["tick_count"] % 50 == 0:
        #TODO: See if we need to put something here?
        pass
    _control_tick_3v3_bus_data["tick_count"] += 1
    return True

def _control_tick_5v_bus(datastore: Datastore):
    #TODO: implement this logic
    return True

def _control_tick_12vlp_bus(datastore: Datastore):
    #TODO: implement this logic
    return True

def _control_tick_12vhp_bus(datastore: Datastore):
    #TODO: implement this logic
    return True