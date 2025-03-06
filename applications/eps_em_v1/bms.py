"""
Module to operate the battery management system.
"""

import asyncio

from datastore import Datastore


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
