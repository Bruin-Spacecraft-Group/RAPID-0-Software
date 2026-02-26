"""
This is an artifact for a simple frequencyio test on the nucleo
using the waveform generator and the serial monitor to see how/whether frequency is
properly interpreted
"""

import microcontroller as mc
import frequencyio
import asyncio

fp = frequencyio.FrequencyIn(mc.pin.PA01)

print("code running")

if __name__ == "__main__":
    print(fp.value)
    while True:
        print(fp.value)

        asyncio.sleep(0.5)
