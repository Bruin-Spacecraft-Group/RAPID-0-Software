"""
This is an artifact for a simple frequencyio test on the nucleo
using the waveform generator and the serial monitor to see how/whether frequency is
properly interpreted
"""

import microcontroller as mc
import frequencyio
import asyncio
import pulseio

fp = frequencyio.FrequencyIn(mc.pin.PA00)

pi = pulseio.PulseIn(mc.pin.PA01)

print("code running")

async def frequency():
    while True:
        
        print(fp.value)

        fp.clear()

        await asyncio.sleep(0.5)

asyncio.run(frequency())
