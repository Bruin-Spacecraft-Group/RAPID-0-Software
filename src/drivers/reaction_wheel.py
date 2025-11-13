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
        
    def get_duty_cycle(self):
        """
        Returns the duty cycle value of the motor pwm
        """
        return self.unsoll.duty_cycle
    
    def get_direction(self):
        """
        Returns motor direction
        True if Clockwise, False if Anticlockwise
        """
        return self.diro.value
    
    def set_duty_cycle(self, dc):
        """
        Sets duty cycle and direction (velocity)
        Positive dc values are clockwise and Negative values anticlockwise
        """
        if dc >= 0:
            self.diro.value = True # Clockwise
            self.unsoll.duty_cycle = dc
        elif dc < 0:
            self.diro.value = False # counterclockwise
            self.unsoll.duty_cycle = -dc
