"""
Program to rotate satellite by a certain value (degrees).
"""

from unittest.mock import patch
import time
import board
from tasks.adcs.reaction_wheel_pd import reaction_wheel_pd_control as pd
from drivers.reaction_wheel import ReactionWheel as motor


ERROR_MARGIN = 0.1
DELAY = 0.1
SPEED = 50
DESIRED_ANGLE = 90

with patch("drivers.reaction_wheel.ReactionWheel.get_real_speed") as mocked_speed:
    mocked_speed.return_value = 0.0
    est_angle = 0.0
    my_motor = motor(board.unsoll, board.diro, board.fg)
    prev_time = time.monotonic_ns()
    prev_error = 0
    current_error = DESIRED_ANGLE - est_angle

    # PD Control loop for rotation
    while abs(current_error) > ERROR_MARGIN:
        current_time = (
            time.monotonic_ns()
        )  # Initialize time for calculating motor spin time

        # Calculate current angle
        dt = (current_time - prev_time) / 1e9
        current_speed = my_motor.get_real_speed() * 60  # Convert from rpm to rps
        est_angle += current_speed * dt

        current_error = DESIRED_ANGLE - est_angle

        # Update parameters from PD loop
        p_term, d_term, prev_time, prev_error = pd(
            DESIRED_ANGLE, est_angle, prev_error, prev_time
        )

        # Update motor speed to achieve desired angle
        my_motor.set_speed(p_term + d_term)
        current_time = prev_time
        time.sleep(DELAY)

    my_motor.set_speed(0)
