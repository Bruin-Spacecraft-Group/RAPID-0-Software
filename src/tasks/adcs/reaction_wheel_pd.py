"""
Reaction wheel PD control iteration.
"""

import time

"""
Calculations to perform to find p_term and d_term for one iteration of the pd control loop.
"""


def reaction_wheel_pd_control(
    desired_value, current_value, prev_error, prev_time, kp=1, kd=1
):
    # Initialize time and error for current PD Loop iteration
    current_time = time.monotonic_ns()
    error = desired_value - current_value

    # Calculate terms to sum for motor speed
    p_term = kp * error
    dt = (current_time - prev_time) / 1e9  # Convert to seconds
    d_term = kd * (error - prev_error) / dt

    # Return updated parameters for PD Loop
    return p_term, d_term, current_time, error
