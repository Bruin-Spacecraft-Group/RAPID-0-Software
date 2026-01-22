"""
Reaction wheel PD controller loop.
"""

import time

KP = 1
KD = 1
ERROR_MARGIN = 0
DELAY = 10

prev_speed = 0
current_speed = 0


def reaction_wheel_pd_control(desired_speed, motor):

    # Retrieve the initial speed of the motor and start the initial timer
    prev_speed = motor.get_speed()
    prev_time = time.monotonic_ns()

    # Set the current speed to the initial speed of the motor
    current_speed = prev_speed

    # While there is a significant error between the current and desired speed
    while abs(desired_speed - current_speed) > ERROR_MARGIN:

        # Start the timer for the beginning of the PD loop and calculate P and D terms
        current_time = time.monotonic_ns()
        p_term = current_speed * KP
        d_term = KD * (current_speed - prev_speed) / (prev_time - current_time)
        prev_speed = current_speed

        # Reset the initial timer (end of PD loop) and apply changed values to motor speed
        prev_time = time.monotonic_ns()
        motor.set_speed(p_term + d_term)

        # Retrieve the new speed of the motor and implement loop delay
        current_speed = motor.get_speed()
        time.sleep(10)
