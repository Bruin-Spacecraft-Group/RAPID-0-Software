"""
Module of objects and classes which store data pertaining to the current state of the
ADCS system for all tasks to update and use. Readings that have not yet been initialized
are set to `None` throughout this module.
"""


class Datastore:
    """
    Datastore class for adcs processes. Holds time, sensor, and attitude data to be used system-wide
    """

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
        self.update_interval = 1.0  # secondsgit
        self.time_since_last_mekf = 0.0  # dt from tasks/mekf


class sensorData:
    def __init__(self):
        self.sun = None
        self.magnetometer = None
        self.gyroscope = None


class attitudeCalc:
    def __init__(self):
        # reference vectors in inertial frame
        self.ref_vec1 = 0.0  # more accurate vector
        self.ref_vec2 = 0.0  # less accurate vector

        # measures of vectors in body frame
        self.frame_vec1 = 0.0
        self.frame_vec2 = 0.0


class attitudeData:
    def __init__(self):
        q_ref = None  # Reference attitude Quaternion
        w_ref = None  # Reference angular velocity (3x1 vector)
        P = None  # Error covariance matrix (3x3 matrix)
        Q_noise = None  # Process noise covariance matrix (3x3 matrix)
        v_inertial = None  # Expected vector measurement at Quaternion(1,0,0,0) orientation (3x1 vector)
        cv_matrix = None  # Current covariance
        dt = None  # Time step since last update (float)


class TLE:
    def __init__(self):
        self


class SUN:
    def __init__(self):
        pass


class magneticField:
    def __init__(self):
        pass
