"""
Testing module for the reaction wheel and speed controller driver

This is a "dumb" test script for the nucleo h7 board
"""

import microcontroller as mc
# import board
import digitalio
import asyncio
import drivers.reaction_wheel as rw

# import time

print("code running")

# REBOUND = 0.5 # s

# PA0 unsoll, PA1 dir, PA4 fg
sc = rw.ReactionWheel(mc.pin.PA00, mc.pin.PA01, mc.pin.PA04)

# Digital input "USER" button (find pin name)
ub = digitalio.DigitalInOut(mc.pin.PC13)

print("successful init")

speed = 0
lock = asyncio.Lock() # see if this is needed?

async def speed_input():
    while True:
        global speed
        speed = input("0-100: ")

async def run_motor():
    while True:
        global speed
        sc.set_speed_pc(speed)

async def main():
    speed = asyncio.create_task(speed_input())
    run = asyncio.create_task(run_motor())
    await asyncio.gather(speed, run)

    print(speed, sc.get_speed())

if __name__ == "__main__":
    main()
