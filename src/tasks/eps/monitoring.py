"""
Module to monitor the health and state of the EPS system. This includes
* coordinating the reading of data from external analog-to-digital converters in the system
* reading digital data produced by the system
* recording reliability metrics related to system memory faults and restarts as necessary
"""

import asyncio

from datastores.eps import Datastore


async def data_recording_task(datastore: Datastore):
    """
    Task to read all analog and digital data in the system and place it into the `datastore`.
    """
    while True:
        print(datastore)
        await asyncio.sleep(0)
