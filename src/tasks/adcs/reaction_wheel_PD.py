"""
Reaction wheel PD controller loop.
"""

import submodules.Adafruit_CircuitPython_Ticks.adafruit_ticks as timer

KP = 1
KD = 1
ERROR_MARGIN = 0

prev_speed = 0
current_speed = 0


def reaction_wheel_pd_control(desired_speed, motor):

    prev_speed = motor.get_speed()  # temp
    start_time = timer.ticks_ms()

    current_speed = prev_speed

    while abs(desired_speed - current_speed) > ERROR_MARGIN:
        current_speed = motor.get_speed()  # temp
        end_time = timer.ticks_ms()
        p_term = current_speed * KP
        d_term = (
            KD * (current_speed - prev_speed) / timer.ticks_diff(end_time, start_time)
        )
        prev_speed = current_speed
        start_time = timer.ticks_ms()
        motor.set_speed(p_term + d_term)
        current_speed = motor.get_speed()
