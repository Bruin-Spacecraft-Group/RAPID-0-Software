import asyncio
from tasks import inter_subsystem_rs485

async def gathered_task():
    """Runs all tasks in parallel."""
    await asyncio.gather(
        inter_subsystem_rs485.nucleo_rs485_reciever_task()
    )

if __name__ == "__main__":
    # with open("/sus.txt", "a") as fp:
    #     fp.write("Wow I can't believe it worked!")
    asyncio.run(gathered_task())
    print('CDH code.py has been run successfully.')
