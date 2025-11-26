"""
Testing module for the reaction wheel and speed controller driver on the CDH board
"""

import microcontroller as mc
import drivers.reaction_wheel as rw

import analogio as an

import board
import sdcardio as sd
import storage

import circuitpython_csv as csv

import time
import ulab.numpy as np

print("code running")

class Pins:
    """
    Pins used in the testing
    """

    # speed controler/motor setup
    unsoll = mc.pin.PA01

    diro = mc.pin.PB01
    fg = mc.pin.PA02

    # input pin from accelerometer
    acc = 0

    # sd card pin
    sd = 0

    # TODO: Figure out if this is how we should handle optical encoder
    opt = 0

# program constants
SAMPLE_RATE = 500 # ms
TIME = 10 # s
MAX = 2**16 - 1

ORIGIN = 0

# PA1 unsoll, PB1 dir, PA2 fg
sc = rw.ReactionWheel(Pins.unsoll, Pins.diro, Pins.fg)
a = an.AnalogIn(Pins.acc)
optical = an.AnalogIn(Pins.opt)

# initialise sd
spi = board.SPI()
sdcard = sd.SDCard(spi, Pins.sd)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

print("successful init")

def const_meas(length: int, sample_rate: int):
    """
    First measurement case with constant speed measuring acceleration and position
    
    :param length: constant time to run program for (seconds)
    :type length: int
    :param sample_rate: delay between measurements (ms)
    :type sample_rate: int

    returns matrix of 3 columns, parallel arrays times [0] accel [1] pos [2]
    """
    times = []
    accel = []
    pos = []
    t = 0

    while t <= length:
        sc.set_speed(2**12)
        
        t = time.perf_counter()

        if (t*1000) % sample_rate:
            times.append(t)
            accel.append(a.value)
            pos.append(optical.value)

    return [times, accel, pos]

def var_speed_meas(length: int, sample_rate: int):
    """
    Second measurement case varying speed and measuring acceleration and position
    
    :param length: constant time to run program for (seconds)
    :type length: int
    :param sample_rate: delay between measurements (ms)
    :type sample_rate: int

    :return: matrix of 4 columns, parallel arrays speeds [0] times [1] accel [2] pos [3]
    :rtype: list[4]
    """
    speeds = []
    times = []
    accel = []
    pos = []
    t = 0

    steps = np.arange(5, 100, 5)

    for s in steps:
        s = s * 0.01
        speeds.append(s)

        # measurement lasts for TIME (10) seconds
        while t <= length:
            # set speed with increments 0.05 to 1.00 with 0.05 increments
            sc.set_speed(MAX * s)

            t = time.perf_counter()

            if (t*1000) % sample_rate == 0:
                times.append(t)
                accel.append(a.value)
                pos.append(optical.value)

    return [speeds, times, accel, pos]

def sin_meas(length: int, sample_rate: int) -> list:
    """
    Third sinusoidal speed profile measuring torque output with respect to speed
    
    :param length: Description
    :type length: int
    :param sample_rate: Description
    :type sample_rate: int

    :return: Description
    :rtype: list
    """
    speeds = []
    times = []
    # TODO: Figure out what exactly needs to be exported/calculated here

    t=0

    while t <= length:
        # period of 2pi seconds
        sc.set_speed(np.sin(t))
        
        t = time.perf_counter()


def write_to_csv(name: str, headers: list[str], values: list) -> None:
    """
    Creates CSV files on the board SD card to be exported into excel
    
    :param name: name of the csv to export
    :type name: str
    :param headers: list of headers
    :type headers: list[str]
    :param values: value matrix indexed respective to headers
    :type values: list
    """

    # flip values list 90 degrees
    values = list(map(list, zip(*values)))

    with open(f"/sd/${name}.csv", "w", encoding='utf-8') as wr:
        csvwriter = csv.writer(wr)
        csvwriter.writerow(headers)

        for row in values:
            csvwriter.writerow(row)

if __name__ == "__main__":
    write_to_csv("meas1-const", ["time", "accel", "position"], const_meas())
    write_to_csv("meas2-var", ["speed", "time", "accel", "position"], var_speed_meas())
    write_to_csv("meas3-sin", [], sin_meas())
