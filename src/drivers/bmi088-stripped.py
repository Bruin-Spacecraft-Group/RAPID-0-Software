"""
Stripped implementation of the bmi088 SPI driver
"""

import asyncio
import time
import digitalio
import busio

class Bmi088Gyroscope:
    """
    Only for the gyroscope in the IMU
    """

    
