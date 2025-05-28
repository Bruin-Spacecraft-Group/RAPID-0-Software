"""
Entry point for a testing artifact that simulates the CDH microcontroller on
a custom breakout board.
"""

import asyncio
import inter_subsystem_rs485

async def gathered_task():
    """
    Task to run all other tasks concurrently.
    """
    await asyncio.gather(inter_subsystem_rs485.inter_subsystem_rs485_sender_task())

if __name__ == "__main__":
    asyncio.run(gathered_task())
