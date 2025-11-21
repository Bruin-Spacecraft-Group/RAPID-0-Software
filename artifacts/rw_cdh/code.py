"""
Testing module for the reaction wheel and speed controller driver on the CDH board
"""

import microcontroller as mc
import drivers.reaction_wheel as rw

print("code running")

# PA1 unsoll, PB1 dir, PA2 fg
sc = rw.ReactionWheel(mc.pin.PA01, mc.pin.PB01, mc.pin.PA02)

print("successful init")

if __name__ == "__main__":
    while True:
        sc.set_speed(2**15)
        print(sc.get_speed(), sc.get_direction())
