"""
Artifact to be run on the CDH Engineering Model Board
"""

import asyncio
from inter_subsystem_rs485 import cdh_em_board_rs485_send_task

async def gathered_task():
    """
    Task to run all other tasks concurrently.
    """
    await asyncio.gather(
        cdh_em_board_rs485_send_task()
    )


if __name__ == "__main__":
    asyncio.run(gathered_task())
    print('CDH code.py has been run successfully.')
