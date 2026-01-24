"""
Testing module for the reaction wheel and speed controller driver

This is a "dumb" test script for the nucleo h7 board
"""

import microcontroller as mc
import board
import busio

import digitalio
import drivers.reaction_wheel as rw

# import time

print("code running")

# REBOUND = 0.5 # s

# PA0 unsoll, PA1 dir, PA4 fg
sc = rw.ReactionWheel(mc.pin.PA00, mc.pin.PA01, mc.pin.PA04)

# Digital input "USER" button (find pin name)
ub = digitalio.DigitalInOut(mc.pin.PC13)

# accelerometer is connected for i2c where:
# SCL(K), SDA/I is connected to respective SCL SDA
# AD0, Fsync is gnd
# INT is connected to PB00 (unnecessary for now)
i2c = busio.I2C(board.SCL, board.SDA)

while not i2c.try_lock():
    pass

# verify bus address 0x68
print([hex(x) for x in i2c.scan()])

def safe_convert(value, target_type):
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return None

def read_accel():
    # input is apparently 0x68,
    # output registers are 59 to 64 (0x3A to 0x3F)
    result = bytearray(6)
    registers = [0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F]
    # xH, xL, yH, yL, zH, zL

    for r in registers:
        i2c.writeto_then_readfrom(0x68, bytes([r]), result)
    
    print(result[0] << 8)
    # from result, combine into readable decimal array
    def combine(h, l):
        return (result[h] << 8) + result[l]
    
    # into decimal
    ret = [combine(0, 1), combine(2, 3), combine(4, 5)]

    print(ret)

    return result

print("successful init")

if __name__ == "__main__":
    speed = 0
    while True:
        sc.set_speed_pc(speed)

        usr = input("cmd: ")

        if safe_convert(usr, float) != None:
            speed = float(usr)
        else:
            cmd = usr.strip() 
            if cmd == "accel":
                print("accel: ", str(read_accel()))
            elif cmd == "help":
                print(
    """function list:
accel - returns accelerometer data
[-100, 100] - any numerical input spins motor at percentage speed
help - prints this message
    """)
            
i2c.unlock()
