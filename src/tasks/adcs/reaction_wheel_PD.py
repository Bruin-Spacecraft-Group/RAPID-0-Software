"""
Reaction wheel PD controller loop.
"""

import time

KP = 1
KD = 1
ERROR_MARGIN = 0
DELAY = 0.5


def reaction_wheel_pd_control(desired_speed, motor):
    # Set the current speed to the initial speed of the motor
    current_speed = motor.get_speed()

    # Initialize prev_error to be the current error
    prev_error = desired_speed - current_speed

    # Start the initial timer
    prev_time = time.monotonic_ns()

    # While there is a significant error between the current and desired speed
    while abs(desired_speed - current_speed) > ERROR_MARGIN:
        # Calculate current error and get the current time
        error = desired_speed - current_speed
        current_time = time.monotonic_ns()

        # Calculate terms to sum for motor speed
        p_term = KP * error
        dt = (current_time - prev_time) / 1e9  # Convert to seconds
        d_term = KD * (error - prev_error) / dt

        # Update motor speed
        motor.set_speed(p_term + d_term)

        # Update prev_error to the current error
        prev_error = error

        # Retrieve the new speed of the motor and implement loop delay
        time.sleep(DELAY)
        current_speed = motor.get_speed()

        # Update prev_time to the time of finishing this iteration
        prev_time = time.monotonic_ns()
