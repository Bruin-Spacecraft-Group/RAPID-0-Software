"""
Entry point for a testing artifact that simulates the CDH microcontroller on
a custom SamD51 breakout board.
"""

import asyncio
import microcontroller
from inter_subsystem_rs485 import cdh_em_board_rs485_receiver_task

async def gathered_task():
    """
    Task to run all other tasks concurrently.
    """
    await asyncio.gather(
        cdh_em_board_rs485_receiver_task(microcontroller.pin.PA00, microcontroller.pin.PA01, microcontroller.pin.PA02)
    )


if __name__ == "__main__":
    asyncio.run(gathered_task())
    print('CDH code.py has been run successfully.')
