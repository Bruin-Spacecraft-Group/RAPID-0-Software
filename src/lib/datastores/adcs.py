"""
Module of objects and classes which store data pertaining to the current state of the
ADCS system for all tasks to update and use. Readings that have not yet been initialized
are set to `None` throughout this module.
"""


class Datastore:
    """ """

    DETUMBLE = 0
    POINT_TO_SUN = 1
    POINT_TO_EARTH = 2
    NOMINAL_PROCESSES = 3

    def __init__(self):
        self.time: adcsTime = adcsTime()
        self.sensor: sensorData = sensorData() 
        self.quaternion = (
            None  # Quaternion representing attitude from body frame to inertial frame
        )
        self.mode = 0


class adcsTime: 
    def __init__(self): 
        self.current_time = None
        self.last_cdh_update = None
        self.update_interval = 1.0 # secondsgit

class sensorData: 
    def __init__(self): 
        self.sun = None
        self.magnetometer = None 
        self.gyroscope = None 

