"""
Testing module for the reaction wheel and speed controller driver
"""

import microcontroller as mc
import drivers.reaction_wheel as rw

# PA0 unsoll, PA1 dir, PA4 fg
sc = rw.ReactionWheel(mc.pin.PA0, mc.pin.PA1, mc.PA4)

if __name__ == "__main__":
    sc.set_speed(2**7)
