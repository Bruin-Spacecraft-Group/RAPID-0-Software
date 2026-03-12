"""
Testing code for reaction wheels using PD control loop.
"""

from unittest.mock import patch
import time
import board
from tasks.adcs.reaction_wheel_pd import reaction_wheel_pd_control as pd
from drivers.reaction_wheel import ReactionWheel as motor


KP = 1
KD = 1
ERROR_MARGIN = 0.1
DELAY = 0.1
DESIRED_VALUE = 50

with patch("drivers.reaction_wheel.ReactionWheel.get_speed") as mocked_speed:
    mocked_speed.return_value = 0.0
    my_motor = motor(board.unsoll, board.diro, board.fg)
    prev_time = time.monotonic_ns()
    prev_error = 0
    current_speed = my_motor.get_speed()
    current_error = DESIRED_VALUE - current_speed

    # PD Control loop for motor speed
    while abs(current_error) > ERROR_MARGIN:

        # Initialize motor speed and current error
        current_speed = my_motor.get_speed()
        current_error = DESIRED_VALUE - current_speed

        # Update parameters from PD loop
        p_term, d_term, prev_time, prev_error = pd(
            DESIRED_VALUE, current_speed, prev_error, prev_time
        )

        # Update motor speed to achieve desired speed
        my_motor.set_speed(p_term + d_term)
        time.sleep(DELAY)

    my_motor.set_speed(0)
