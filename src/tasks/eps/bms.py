"""
Module to operate the battery management system.
"""

import asyncio

from datastores.eps import Datastore

MEASURABLE_DIFF_V = 1
SIGNIFICANT_DIFF_V = 10

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
    """Apply balancing logic to one 2-cell battery string."""

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
    string.top_balancing_shunt_enabled = False
    string.bottom_balancing_shunt_enabled = False


def handle_top_on(string, v_a, v_b):
    if v_b > v_a + MEASURABLE_DIFF_V:
        string.top_balancing_shunt_enabled = False
    elif v_a > v_b + MEASURABLE_DIFF_V:
        string.bottom_balancing_shunt_enabled = True


def handle_bottom_on(string, v_a, v_b):
    if v_a > v_b + MEASURABLE_DIFF_V:
        string.bottom_balancing_shunt_enabled = False
    elif v_b > v_a + MEASURABLE_DIFF_V:
        string.top_balancing_shunt_enabled = True


def handle_both_off(string, v_a, v_b):
    if v_a > v_b + SIGNIFICANT_DIFF_V:
        string.top_balancing_shunt_enabled = True
        string.bottom_balancing_shunt_enabled = False
    elif v_b > v_a + SIGNIFICANT_DIFF_V:
        string.bottom_balancing_shunt_enabled = True
        string.top_balancing_shunt_enabled = False
    else:
        string.top_balancing_shunt_enabled = False
        string.bottom_balancing_shunt_enabled = False
