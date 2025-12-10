"""
Testing module for the reaction wheel and speed controller driver
"""

import microcontroller as mc
import drivers.reaction_wheel as rw
import time

print("code running")

# PA0 unsoll, PA1 dir, PA4 fg
sc = rw.ReactionWheel(mc.pin.PA00, mc.pin.PA01, mc.pin.PA04)

print(mc.pin)

print("successful init")

if __name__ == "__main__":
    while True:
        SPEED = 0.2
        sc.set_speed(-int(2**15 * SPEED))

        # also good time to test if this logic is correct
        if ((time.perf_counter()*1000) % 500 == 0):
            print(f"S: ${sc.get_speed()}, M: ${sc.get_real_speed()}")
