"""
Program to rotate satellite by a certain value (degrees).
"""

import board
import time
from tasks.adcs.reaction_wheel_PD import reaction_wheel_pd_control as pd
from drivers.reaction_wheel import ReactionWheel as motor

KP = 1
KD = 1
ERROR_MARGIN = 0.1
DELAY = 0.1
SPEED = 50
DESIRED_ANGLE = 90

est_angle = 0.0
my_motor = motor(board.unsoll, board.diro, board.fg)
prev_time = time.monotonic_ns()
prev_error = 0

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
        DESIRED_ANGLE, est_angle, prev_error, prev_time, KP, KD
    )

    # Update motor speed to achieve desired angle
    my_motor.set_speed((p_term + d_term))
    current_time = prev_time
    time.sleep(DELAY)

motor.set_speed(0)
