"""
Testing code for reaction wheels using PD control loop.
"""

import board
from tasks.adcs.reaction_wheel_PD import reaction_wheel_pd_control as pd
from drivers.reaction_wheel import ReactionWheel as motor


KP = 1
KD = 1
ERROR_MARGIN = 0.1
DELAY = 0.1

my_motor = motor(board.unsoll, board.diro, board.fg)

pd(50, my_motor, ERROR_MARGIN, KP, KD, DELAY)

motor.set_speed(0)
