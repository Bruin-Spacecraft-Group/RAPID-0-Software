"""
Testing module for the reaction wheel and speed controller driver

This is a "dumb" test script for the nucleo h7 board
"""

import microcontroller as mc
import board
import drivers.reaction_wheel as rw
import digitalio
import time

print("code running")

REBOUND = 100 # ms

# PA0 unsoll, PA1 dir, PA4 fg
sc = rw.ReactionWheel(mc.pin.PA00, mc.pin.PA01, mc.pin.PA04)

# Digital input "USER" button (find pin name)
ub = digitalio.DigitalInOut(mc.pin.PC13)

print("successful init")

if __name__ == "__main__":
    t = 0.0
    speed = 1.0 # full speed
    while True:
        sc.set_speed(int((2**16 - 1) * speed))
        
        # temp for current time just in case of scripting language quirks
        curr = time.perf_counter()

        if ub.value and curr - t >= REBOUND:
            t = curr

            # cycle from full - half - quarter - rest
            if speed == 1.0:
                speed = 0.5
            elif speed == 0.5:
                speed = 0.25
            elif speed == 0.25:
                speed = 0.0
            else:
                speed = 1.0

 