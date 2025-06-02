import asyncio
from tasks.camera_tasks import capture_single_image

async def gathered_task():
    """Runs all tasks in parallel."""
    await asyncio.gather(
        capture_single_image(return_bursts = False)
    )


if __name__ == "__main__":
    # asyncio.run(gathered_task())
    print('CDH code.py has been run successfully.')