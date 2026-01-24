"""
This is an artifact for a simple frequencyio test on the nucleo
using the waveform generator and the serial monitor to see how/whether frequency is
properly interpreted
"""

import microcontroller as mc
import frequencyio

fp = frequencyio.FrequencyIn(mc.pin.PA00)

print("code running")

if __name__ == "__main__":
    while True:
        print(fp.value())

        fp.clear()
