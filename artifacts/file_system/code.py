"""
Code to open a file and do UART communication on a nucleo board.
"""

import asyncio
import board
import microcontroller
from inter_subsystem_rs485 import nucleo_rs485_sender_task


async def gathered_task():
    """Runs all tasks in parallel."""
    await asyncio.gather(
        nucleo_rs485_sender_task(
            microcontroller.pin.PD05,
            microcontroller.pin.PD06,
            microcontroller.pin.PD07,
            board.LED1,
        )
    )


if __name__ == "__main__":
    with open("/sus.txt", "a", encoding="utf-8") as fp:
        fp.write("Wow I can't believe it worked!")
    asyncio.run(gathered_task())
    print("CDH code.py has been run successfully.")
