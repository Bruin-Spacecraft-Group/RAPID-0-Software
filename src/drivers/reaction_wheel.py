"""
Driver module for the 1509T012B reaction wheel motor using the SC 1801 P speed controller
"""

import pwmio
import digitalio
# import frequencyio

class ReactionWheel:
    """
    Reaction wheel class that includes speed controller
    """

    def __init__(self, unsoll, diro, fg):
        """
        Reaction wheel class instance
        
        :param unsoll: PWM input for speed control
        :param diro: Digital input for direction control
        :param fg: Frequency output for motor encoder data
        """
        self.unsoll = pwmio.PWMOut(unsoll)
        # Digital In - Directional Input
        self.diro = digitalio.DigitalInOut(diro)
        self.diro.direction = digitalio.Direction.OUTPUT
        # Digital Out - Frequency out
        self.fg = fg
        # self.fg = frequencyio.FrequencyIn(fg)

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
        Sets speed by duty cycle and direction
        Positive dc values are clockwise and Negative values anticlockwise
        
        :param dc: from domain [-2^16 to 2^16]
        """

        if dc >= 0:
            self.diro.value = True # Clockwise
            self.unsoll.duty_cycle = dc
        elif dc < 0:
            self.diro.value = False # counterclockwise
            self.unsoll.duty_cycle = -dc

    def set_speed_pc(self, pc: float):
        """
        Sets speed by percentage and direction. 
        Positive values clockwise, Negative values anticlockwise

        :param pc: from domain [-100 to 100]
        """
        maxs = 2**16-1

        self.set_speed(int((pc/100) * maxs))

    def get_real_speed(self):
        """
        Reads hall sensors to gauge the real speed the motor is spinning at in rpm

        Returns result in rpm
        """

        # frequencyIn testing for now

        return self.fg.value
