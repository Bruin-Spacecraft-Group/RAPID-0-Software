"""
Software entry point for the control application for the EPS flatsat PCB from June 2024.
"""

import asyncio

import bms
import icd
import monitoring

import datastore as ds

datastore = ds.Datastore()


async def gathered_task():
    """
    Runs all top-level tasks in parallel.

    Currently includes battery management, output bus control, data recording to the `datastore`,
    and intersubsystem communication.
    """
    await asyncio.gather(
        bms.battery_management_task(datastore),
        icd.output_bus_control_task(datastore),
        monitoring.data_recording_task(datastore),
        icd.intersubsystem_communication_task(datastore),
    )


if __name__ == "__main__":
    # TODO: uncomment to run flight code (only once the electrical parts of the PCB are validated)
    # asyncio.run(gathered_task())

    # import board
    import digitalio

    # TODO: uncomment pins to run electrical tests and validate the PCB
    for BMS_SHD in [
        # board.S1_CHARGE_SHD,
        # board.S1_DISCHARGE_SHD,
        # board.S2_CHARGE_SHD,
        # board.S2_DISCHARGE_SHD,
        # board.S3_CHARGE_SHD,
        # board.S3_DISCHARGE_SHD,
    ]:
        pin = digitalio.DigitalInOut(BMS_SHD)
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = False
    for EN_PSU in [
        # board.EN_3V3_BUS,
        # board.EN_5V_BUS,
        # board.EN_12VLP_BUS,
        # board.EN_12VHP_BUS,
        # board.MPPT_EN
    ]:
        pin = digitalio.DigitalInOut(EN_PSU)
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = True
        # nda_libraries.run_if_nda_libraries_available(run_secret_functions)
    while True:
        pass
