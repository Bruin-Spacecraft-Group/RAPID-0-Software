"""
Reaction wheel PD control iteration.
"""

import time

KP = 0.01
KD = 0.01


def reaction_wheel_pd_control(desired_value, current_value, prev_error, prev_time):
    """Calculations to perform to find p_term and d_term for one iteration of the pd control loop."""

    # Initialize time and error for current PD Loop iteration
    current_time = time.monotonic_ns()
    error = desired_value - current_value

    # Calculate terms to sum for motor speed
    p_term = KP * error
    dt = (current_time - prev_time) / 1e9  # Convert to seconds
    d_term = KD * (error - prev_error) / dt

    # Return updated parameters for PD Loop
    return p_term, d_term, current_time, error
