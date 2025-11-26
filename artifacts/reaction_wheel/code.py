"""
Testing module for the reaction wheel and speed controller driver
"""

import microcontroller as mc
import drivers.reaction_wheel as rw

print("code running")

# PA0 unsoll, PA1 dir, PA4 fg
sc = rw.ReactionWheel(mc.pin.PA00, mc.pin.PA01, mc.pin.PA04)

print("successful init")

if __name__ == "__main__":
    while True:
        sc.set_speed(2**12)
        print(sc.get_speed(), sc.get_direction())
