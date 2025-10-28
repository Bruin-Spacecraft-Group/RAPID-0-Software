"""
Module to operate the battery management system.
"""

import asyncio

from datastores.eps import Datastore


async def battery_management_task(datastore: Datastore):
    """
    Asynchronous control loop for battery balancing.

    Uses the latest readings in `datastore` as inputs and updates
    balancing control flags for each battery string accordingly.
    """
    while True:
        balance_all_strings(datastore)
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


def balance_single_string(string):
    """
    Apply balancing logic to one 2-cell battery string.

    Based on:
    - Whether string is charging and nearly full
    - Difference in cell voltages
    - Current balancing switch states
    """

    v_a = string.top_cell_voltage
    v_b = string.bottom_cell_voltage

    # Skip if voltages not yet initialized
    if v_a is None or v_b is None:
        return

    # Determine if charging and near full (placeholder logic)
    charging = True
    almost_full = max(v_a, v_b) > 4.15  # near-full threshold example

    if charging and almost_full:
        a_on = string.top_balancing_shunt_enabled
        b_on = string.bottom_balancing_shunt_enabled

        # --- Case 1: Top cell shunt is ON ---
        if a_on:
            if v_b > v_a + MEASURABLE_DIFF_V:
                string.top_balancing_shunt_enabled = False
            elif v_a > v_b + MEASURABLE_DIFF_V:
                string.bottom_balancing_shunt_enabled = True

        # --- Case 2: Bottom cell shunt is ON ---
        elif b_on:
            if v_a > v_b + MEASURABLE_DIFF_V:
                string.bottom_balancing_shunt_enabled = False
            elif v_b > v_a + MEASURABLE_DIFF_V:
                string.top_balancing_shunt_enabled = True

        # --- Case 3: Neither shunt ON ---
        else:
            if v_a > v_b + SIGNIFICANT_DIFF_V:
                string.top_balancing_shunt_enabled = True
                string.bottom_balancing_shunt_enabled = False
            elif v_b > v_a + SIGNIFICANT_DIFF_V:
                string.bottom_balancing_shunt_enabled = True
                string.top_balancing_shunt_enabled = False
            else:
                string.top_balancing_shunt_enabled = False
                string.bottom_balancing_shunt_enabled = False

    else:
        # Not charging or not full → disable all balancing
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = False