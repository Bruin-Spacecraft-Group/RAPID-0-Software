"""
This is an artifact for a simple frequencyio test on the nucleo
using the waveform generator and the serial monitor to see how/whether frequency is
properly interpreted
"""

import microcontroller as mc
import frequencyio
import asyncio

fp = frequencyio.FrequencyIn(mc.pin.PA00)

print("code running")

async def frequency():
    while True:
        
        print(fp.value)

        await asyncio.sleep(0.5)

asyncio.run(frequency())
