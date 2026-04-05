"""
Driver module for the DRV8876 H-Bridge Motor Driver
"""

import digitalio
import analogio
import pwmio


class HBridge:
    """ """

    def __init__(self, en, nsleep, ph, out1, out2):
        # either in1 or en, identically input
        self.en = digitalio.DigitalInOut(en)
        self.en.direction = digitalio.Direction.INPUT

        # either in2 or ph
        self.ph = digitalio.DigitalInOut(ph)
        self.ph.direction = digitalio.Direction.INPUT

        self.nsleep = digitalio.DigitalInOut(nsleep)
        self.nsleep.direction = digitalio.Direction.INPUT

        self.out1 = digitalio.DigitalInOut(out1)
        self.out1.direction = digitalio.Direction.OUTPUT

        self.out2 = digitalio.DigitalInOut(out2)
        self.out2.direction = digitalio.Direction.OUTPUT

    def spin(self, d):
        """
        The magnetorquer is set to spin either in fwd (1) brake (0) or rev (-1) mode
        """

        match d:
            case 1:
                pass
            case 0:
                pass
            case -1:
                pass
        pass
