"""
Entry point for a testing artifact that simulates the CDH microcontroller on
a custom SamD51 breakout board.
"""

import asyncio
from inter_subsystem_rs485 import samd51_breakout_receiver_task

async def gathered_task():
    """
    Task to run all other tasks concurrently.
    """
    await asyncio.gather(
        samd51_breakout_receiver_task()
    )


if __name__ == "__main__":
    asyncio.run(gathered_task())
    print('CDH code.py has been run successfully.')
