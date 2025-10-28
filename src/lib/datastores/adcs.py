"""
Module of objects and classes which store data pertaining to the current state of the
ADCS system for all tasks to update and use. Readings that have not yet been initialized
are set to `None` throughout this module.
"""

class Datastore:
    """
    Datastore class for adcs processes. Holds time, sensor, and attitude data to be used system-wide
    """

    # Action types
    DETUMBLE = 0
    POINT_TO_SUN = 1
    POINT_TO_EARTH = 2
    NOMINAL_PROCESSES = 3

    # Constant matrices for MEKF
    CV_MATRIX = (
        None
    )
    GYRO_NOISE = (
        None
    )
    MEAS_NOISE = (
        None
    )

    def __init__(self):
        self.time: AdcsTime = AdcsTime()
        self.sensor: SensorData = SensorData()
        self.quaternion = (
            None  # Quaternion representing attitude from body frame to inertial frame
        )
        self.mode = 0

class AdcsTime:
    """
    Time helper class
    """
    def __init__(self):
        self.current_time = None
        self.last_cdh_update = None
        self.update_interval = 1.0  # secondsgit
        self.time_since_last_mekf = 0.0  # dt from tasks/mekf

class SensorData:
    """
    Sensor helper class
    """
    def __init__(self):
        self.sun = None
        self.magnetometer = None
        self.gyroscope = None

class AttitudeCalc:
    """
    Attitude helper class
    """
    def __init__(self):
        # reference vectors in inertial frame
        self.ref_vec1 = 0.0 # more accurate vector
        self.ref_vec2 = 0.0 # less accurate vector
