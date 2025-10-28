"""
Module to operate the battery management system.
"""

import asyncio

from datastores.eps import Datastore


async def battery_management_task(datastore: Datastore):
    """
    Task which controls string protection and balancing circuits.

    Uses the most recent data in the `datastore` as inputs. Controls circuits to cutoff
    charging and discharging for each battery string. Also controls when power is dissipated
    from each individual cell to maintain a balanced battery pack.
    """
    while True:
        print(datastore)
        await asyncio.sleep(0)

def is_charging_and_almost_full():
    # Some kind of if else to check if almost full and charging
    if():
        return True
    return False

def cell_A_balancing_switch_on():
    # Some kind of if else to check if balancing switch is on
    if():
        return True
    return False

def cell_B_balancing_switch_on():
    # Some kind of if else to check if balancing switch is on
    if():
        return True
    return False

def get_voltage_cell_A():
    #Returns voltage of cell A
    return 0

def get_voltage_cell_B():
    #Returns voltage of cell B
    return 0

def voltage_measurably_larger(cell_A, cell_B):
    #Returns True if voltage A is measurably larger than voltage B
    if(cell_A > cell_B):
        return True
    return False

def voltage_significantly_larger(cell_A, cell_B):
    #Returns True if voltage A is significantly larger than voltage B
    if(cell_A > cell_B):
        return True
    return False

def disable_cell_A_balancing_switch():
    #Disables balancing switch for cell A
    print("Disabling balancing switch for cell A")

def disable_cell_B_balancing_switch():
    #Disables balancing switch for cell B
    print("Disabling balancing switch for cell B")
def enable_cell_A_balancing_switch():
    #Enables balancing switch for cell A
    print("Enabling balancing switch for cell A")
def enable_cell_B_balancing_switch():
    #Enables balancing switch for cell B
    print("Enabling balancing switch for cell B")

def string_balancing_check():

    voltage_A = get_voltage_cell_A()
    voltage_B = get_voltage_cell_B()

    if not is_charging_and_almost_full():
        disable_cell_A_balancing_switch()
        disable_cell_B_balancing_switch()
    else:
        if(cell_A_balancing_switch_on()):
            if(voltage_measurably_larger(voltage_A, voltage_B)):
                disable_cell_B_balancing_switch()
                enable_cell_A_balancing_switch()
                return
            elif(voltage_significantly_larger(voltage_A, voltage_B)):
                disable_cell_B_balancing_switch()
                enable_cell_A_balancing_switch()
                return
            elif(voltage_significantly_larger(voltage_B, voltage_A)):
                disable_cell_A_balancing_switch()
                enable_cell_B_balancing_switch()
                return
            else:
                disable_cell_A_balancing_switch()
                disable_cell_B_balancing_switch()
                return
        elif(cell_B_balancing_switch_on()):
            if(voltage_measurably_larger(voltage_B, voltage_A)):
                disable_cell_A_balancing_switch()
                enable_cell_B_balancing_switch()
                return
            elif(voltage_significantly_larger(voltage_A, voltage_B)):
                disable_cell_B_balancing_switch()
                enable_cell_A_balancing_switch()
                return
            elif(voltage_significantly_larger(voltage_B, voltage_A)):
                disable_cell_A_balancing_switch()
                enable_cell_B_balancing_switch()
                return
            else:
                disable_cell_A_balancing_switch()
                disable_cell_B_balancing_switch()
                return
        else:
            if(voltage_significantly_larger(voltage_A, voltage_B)):
                disable_cell_B_balancing_switch()
                enable_cell_A_balancing_switch()
                return
            elif(voltage_significantly_larger(voltage_B, voltage_A)):
                disable_cell_A_balancing_switch()
                enable_cell_B_balancing_switch()
                return
            else:
                disable_cell_A_balancing_switch()
                disable_cell_B_balancing_switch()
                return

