"""
Entry point for a testing artifact that simulates the a subsystem's microcontroller
which may talk to CDH. This testing artifact runs on a custom breakout board.
"""

import asyncio
from inter_subsystem_rs485 import cdh_em_board_rs485_receiver_task

async def gathered_task():
    """
    Task to run all other tasks concurrently.
    """
    await asyncio.gather(cdh_em_board_rs485_receiver_task())

if __name__ == "__main__":
    asyncio.run(gathered_task())
