"""
Entry point for a testing artifact that simulates the a subsystem's microcontroller
which may talk to CDH. This testing artifact runs on a custom breakout board.
"""

import asyncio
import board
from inter_subsystem_rs485 import cdh_em_board_rs485_receiver_task

async def gathered_task():
    """
    Task to run all other tasks concurrently.
    """
    await asyncio.gather(cdh_em_board_rs485_receiver_task(board.RS485_1_TX, board.RS485_1_RX, board.RS485_1_DE))

if __name__ == "__main__":
    asyncio.run(gathered_task())
