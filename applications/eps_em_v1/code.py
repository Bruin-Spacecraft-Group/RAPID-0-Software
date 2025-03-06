"""
Software entry point for the control application for the EPS flatsat PCB from June 2024.
"""

import asyncio

import datastore as ds
from bms import battery_management_task
from icd import intersubsystem_communication_task, output_bus_control_task
from monitoring import data_recording_task

datastore = ds.Datastore()


async def gathered_task():
    """
    Runs all top-level tasks in parallel.

    Currently includes battery management, output bus control, data recording to the `datastore`,
    and intersubsystem communication.
    """
    await asyncio.gather(
        battery_management_task(datastore),
        output_bus_control_task(datastore),
        data_recording_task(datastore),
        intersubsystem_communication_task(datastore),
    )


if __name__ == "__main__":
    asyncio.run(gathered_task())
