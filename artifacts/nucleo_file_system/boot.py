"""
Setup code that runs ONCE when the board is turned on. The drive can only be remounted inside of this boot.py file.
To remount the drive again, the board must be restarted. It is possible for a system to occur where the board is
remounted to readonly and cannot be accessed by an external computer; in this case the firmware must be reuploaded to the board
"""

import board
import digitalio
import storage

switch = digitalio.DigitalInOut(board.D32)

switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# If the switch pin is connected to ground CircuitPython can write to the drive
storage.remount("/", readonly=switch.value)
