"""
Testing module for the reaction wheel and speed controller driver

This is a "dumb" test script for the nucleo h7 board
"""

import microcontroller as mc
import digitalio

import reaction_wheel as rw

print("code running")

# PA0 unsoll, PA1 dir, PA4 fg
sc = rw.ReactionWheel(mc.pin.PA00, mc.pin.PA01, mc.pin.PA04)

# Digital input "USER" button PC13
ub = digitalio.DigitalInOut(mc.pin.PC13)

print("successful init")

if __name__ == "__main__":
    speed = input("0-100: ") # full speed 100
    print(speed, sc.get_speed())

    while True:
        sc.set_speed_pc(speed)
