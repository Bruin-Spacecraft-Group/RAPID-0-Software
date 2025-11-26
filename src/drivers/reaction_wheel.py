"""
Driver module for the 1509T012B reaction wheel motor using the SC 1801 P speed controller
"""

import pwmio
import digitalio

class ReactionWheel:
    """
    Reaction wheel class that includes speed controller
    """

    def __init__(self, unsoll, diro, fg):
        self.unsoll = pwmio.PWMOut(unsoll)
        # Digital In - Directional
        self.diro = digitalio.DigitalInOut(diro)
        self.diro.direction = digitalio.Direction.OUTPUT
        # Digital Out - Frequency out
        self.fg = digitalio.DigitalInOut(fg)
        self.fg.direction = digitalio.Direction.INPUT

    def get_speed(self):
        """
        Returns the duty cycle value of the motor (-2^16 to 2^16)
        
        Returns Positive if Clockwise, Negative if Counterclockwise
        """

        dire = 1 if self.get_direction() else -1

        return dire * self.unsoll.duty_cycle

    def get_direction(self):
        """
        Returns motor direction

        Returns True if Clockwise, False if Anticlockwise
        """
        return self.diro.value

    def set_speed(self, dc):
        """
        Sets duty cycle and direction (much like velocity)
        Positive dc values are clockwise and Negative values anticlockwise
        
        Accepts inputs dc from domain [-2^16 to 2^16]
        """
        if dc >= 0:
            self.diro.value = True # Clockwise
            self.unsoll.duty_cycle = dc
        elif dc < 0:
            self.diro.value = False # counterclockwise
            self.unsoll.duty_cycle = -dc
