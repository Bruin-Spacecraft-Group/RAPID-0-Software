import asyncio
import inter_subsystem_rs485

async def gathered_task():
    await asyncio.gather(
        inter_subsystem_rs485.samd51_breakout_receiver_task()
    )


if __name__ == "__main__":
    asyncio.run(gathered_task())
    print('CDH code.py has been run successfully.')