"""
Module to operate the battery management system.
"""

import asyncio

from datastores import eps

# TODO: Tune these thresholds based on testing and battery specs
MEASURABLE_DIFF_V = None
SIGNIFICANT_DIFF_V = None
CHARGING_CURRENT_THRESHOLD_A = None
DISCHARGING_CURRENT_THRESHOLD_A = None
CHARGING_TEMPERATURE_THRESHOLD_C = None
DISCHARGING_TEMPERATURE_THRESHOLD_C = None
CHARGING_VOLTAGE_THRESHOLD_V = None
DISCHARGING_VOLTAGE_THRESHOLD_V = None
BALANCING_VOLTAGE_THRESHOLD_V = None # for checking against each cell separately

async def battery_management_task(datastore: eps.Datastore):
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

# def balance_all_strings(datastore: eps.Datastore):
#     """
#     Apply balancing logic to all battery strings in the pack.
#     """
#     for string in [
#         datastore.batteries.string_1,
#         datastore.batteries.string_2,
#         datastore.batteries.string_3
#     ]:
#         balance_single_string(string)

def string_charge_check(string: eps.DsBatteryString):
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

def string_discharge_check(string: eps.DsBatteryString):
    """
    Check if a battery string is in a safe state for balancing during discharging.

    False to disable, True to enable discharge switch
    """
    if string.output_current > DISCHARGING_CURRENT_THRESHOLD_A:
        return False
    if string.top_cell_voltage > DISCHARGING_VOLTAGE_THRESHOLD_V or string.bottom_cell_voltage > DISCHARGING_VOLTAGE_THRESHOLD_V:
        return False
    for i in string.temperatures:
        if i > DISCHARGING_TEMPERATURE_THRESHOLD_C:
            return False
    return True

def balance_single_string(string: eps.DsBatteryString):
    """Apply balancing logic to one 2-cell battery string."""
    v_a, v_b = string.top_cell_voltage, string.bottom_cell_voltage
    if v_a is None or v_b is None:
        return

    # Check if charging and at least one of the cells are almost fully charged
    if not string.charging_enabled or not (max(string.top_cell_voltage, string.top_cell_voltage) > BALANCING_VOLTAGE_THRESHOLD_V):
        disable_balance(string, "both")
        return

    a_on, b_on = string.top_balancing_shunt_enabled, string.bottom_balancing_shunt_enabled

    diff = 0
    if a_on:
        diff = v_a - v_b
    elif b_on: # noticing that b has opposite logic to a_on
        diff = v_b - v_a
    else: # if neither enabled, skipped logic
        diff = v_a - v_b

        if diff > SIGNIFICANT_DIFF_V:
            disable_balance(string, "b")
        elif diff < 0 - SIGNIFICANT_DIFF_V: # making sure it doesn't think I'm doing unary operator
            disable_balance(string, "a")
        else:
            disable_balance(string, "both")
        return

    # comments with logic in terms of a_on
    if diff > MEASURABLE_DIFF_V:
        # diff greater than measurable, a enable b disable
        disable_balance(string, "b")
        return

    if diff < -MEASURABLE_DIFF_V: # otherwise if diff is negative where b>a, a disable b enable
        disable_balance(string, "a")
    else:
        disable_balance(string, "both")
    
    return

def disable_balance(string: eps.DsBatteryString, disabled_cell: str):
    """
    Helper function to disable balancing shunts based on the cell to be disabled 

    if a disabled b enabled, disabled_cell is a. If both a and b disabled, disabled_cell = both

    disabled_cell has options "a", "b", and "both"
    """

    if disabled_cell == "both":
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = False
        return

    # logic treats as defaults true and disables depending on disabled cell.
    # 1 more call for better readability
    string.top_balancing_shunt_enabled = True
    string.bottom_balancing_shunt_enabled = True

    if disabled_cell == "a":
        string.top_balancing_shunt_enabled = False
    elif disabled_cell == "b":
        string.bottom_balancing_shunt_enabled = False
