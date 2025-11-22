"""
Module to operate the battery management system.
"""

import asyncio


from datastores.eps import Datastore


# TODO: Tune these thresholds based on testing and battery specs
MEASURABLE_DIFF_V = None
SIGNIFICANT_DIFF_V = None
CHARGING_CURRENT_THRESHOLD_A = None
DISCHARGING_CURRENT_THRESHOLD_A = None
CHARGING_TEMPERATURE_THRESHOLD_C = None
DISCHARGING_TEMPERATURE_THRESHOLD_C = None
CHARGING_VOLTAGE_THRESHOLD_V = None
DISCHARGING_VOLTAGE_THRESHOLD_V = None

async def battery_management_task(datastore: Datastore, string):
    """
    Asynchronous control loop for battery balancing.

    Uses the latest readings in `datastore` as inputs and updates
    balancing control flags for each battery string accordingly.
    """
    for string in [
        datastore.batteries.string_1,
        datastore.batteries.string_2,
        datastore.batteries.string_3      
    ]:
        string.discharging_enabled = string_discharge_check(string)
        string.charging_enabled = string_charge_check(string)
        balance_single_string(string)
        await asyncio.sleep(1)  # run once per second
    
    
        
        

def balance_all_strings(datastore: Datastore):
    """
    Apply balancing logic to all battery strings in the pack.
    """
    for string in [
        datastore.batteries.string_1,
        datastore.batteries.string_2,
        datastore.batteries.string_3
    ]:
        balance_single_string(string)

def string_charge_check(string):
    """
    Check if a battery string is in a safe state for balancing during charging.
    """
    if string.output_current < -1*CHARGING_CURRENT_THRESHOLD_A:
        return False
    if string.top_cell_voltage > CHARGING_VOLTAGE_THRESHOLD_V or string.bottom_cell_voltage > CHARGING_VOLTAGE_THRESHOLD_V:
        return False
    for i in string.temperatures:
        if i > CHARGING_TEMPERATURE_THRESHOLD_C:
            return False
    return True

def string_discharge_check(string):
    """
    Check if a battery string is in a safe state for balancing during discharging.
    """
    if string.output_current > DISCHARGING_CURRENT_THRESHOLD_A:
        return False
    if string.top_cell_voltage > DISCHARGING_VOLTAGE_THRESHOLD_V or string.bottom_cell_voltage > DISCHARGING_VOLTAGE_THRESHOLD_V:
        return False
    for i in string.temperatures:
        if i > DISCHARGING_TEMPERATURE_THRESHOLD_C:
            return False
    return True

def balance_single_string(string):
    """Apply balancing logic to one 2-cell battery string."""
    if not string_charge_check(string) or not string_discharge_check(string):
        disable_all_balancing(string)
        return
    v_a, v_b = string.top_cell_voltage, string.bottom_cell_voltage
    if v_a is None or v_b is None:
        return

    # Determine if charging and near full (placeholder logic)
    charging = True
    almost_full = max(v_a, v_b) > 4.15  # near-full threshold example
    if not (charging and almost_full):
        disable_all_balancing(string)
        return

    a_on, b_on = string.top_balancing_shunt_enabled, string.bottom_balancing_shunt_enabled

    if a_on:
        handle_top_on(string, v_a, v_b)
    elif b_on:
        handle_bottom_on(string, v_a, v_b)
    else:
        handle_both_off(string, v_a, v_b)


def disable_all_balancing(string):
    """
    Helper function to disable both balancing shunts
    """
    string.top_balancing_shunt_enabled = False
    string.bottom_balancing_shunt_enabled = False


def handle_top_on(string, v_a, v_b):
    """
    Helper function to handle when the top shunt is enabled and p.d. states change
    """
    if v_a > v_b + MEASURABLE_DIFF_V:
        string.bottom_balancing_shunt_enabled = True
        string.top_balancing_shunt_enabled = False
    elif v_a > v_b + SIGNIFICANT_DIFF_V:
        string.bottom_balancing_shunt_enabled = True
        string.top_balancing_shunt_enabled = False
        
    elif v_b > v_a + SIGNIFICANT_DIFF_V:
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = True
    else:
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = False


def handle_bottom_on(string, v_a, v_b):
    """
    Helper function to handle when the bottom shunt is enabled and p.d. states change
    """
    if v_b > v_a + MEASURABLE_DIFF_V:
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = True
    elif v_a > v_b + SIGNIFICANT_DIFF_V:
        string.bottom_balancing_shunt_enabled = False
        string.top_balancing_shunt_enabled = True
    elif v_b > v_a + SIGNIFICANT_DIFF_V:
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = True
    else:
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = False

def handle_both_off(string, v_a, v_b):
    """
    Helper function to handle when both shunts are off and p.d. states change
    """
    if v_a > v_b + SIGNIFICANT_DIFF_V:
        string.top_balancing_shunt_enabled = True
        string.bottom_balancing_shunt_enabled = False
    elif v_b > v_a + SIGNIFICANT_DIFF_V:
        string.bottom_balancing_shunt_enabled = True
        string.top_balancing_shunt_enabled = False
    else:
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = False
