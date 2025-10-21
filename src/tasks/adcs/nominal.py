"""
Module for ADCS to run nominal operations.
"""

from datastores.adcs import Datastore

from triad import triad_algorithm
from mekf import mekf_update

def get_current_time():
    """
    Placeholder function for getting the current time on satellite
    """

def get_sensor_data() -> tuple[float, ...]:
    """
    Polls sun sensor, magnetometer, and model data for sun and geomagnetic data;
    Polls gyro for angular acceleration
    Returns a tuple of 5 floats with the organisation:
    [sun_sensor, sun_model, magnetometer, mag_model, gyro_alpha]
    """

    return

def nominal_tasks(datastore: Datastore):
    """
    Highest level nominal loop logic
    """

    datastore.current_time = get_current_time()
    
    if datastore.current_time - datastore.last_cdh_update > datastore.update_interval:
        update_attitude(datastore)

        datastore.last_cdh_update = datastore.current_time

def update_attitude(datastore: Datastore):
    """
    Using data from sensors and TRIAD algorithm
    calculates and processes attitude to update datastore values
    """

    # Placeholders for sun sensor data, sun model data, magnetometer data, and geomagnetic model data
    [s_data, s_model,
     mag_data, mag_model,
     alpha] = get_sensor_data()
    
    # sun data is preferred, will be overriden with mag data if not available
    p_data = s_data

    # if sun sensor is unavailable, transition to magnetometer, keep using old quaternion
    if s_data is None:
        p_data = mag_data

        # no quaternion update (?) TODO for operations?
        datastore.quaternion = datastore.quaternion
    else:
        # IFF sun sensor can be used, use TRIAD algorithm to determine attitude from sensor + model data
        [triad_q, msg] = triad_algorithm(s_model, mag_model, s_data, mag_data)

        match msg:
            case 0: # success
                datastore.quaternion = triad_q
            case 1: # anti-parallel
                pass
            case 2: # FAIL : Colinear
                pass
            case 3: # FAIL : Singular (insufficient data)
                pass
            case 4: # FAIL : Normalisation error (div by 0)
                pass
            case _: # catch None or weird case
                pass

    # Clean, update data with MEKF
    datastore.quaternion = mekf_update(
        datastore.quaternion, 
        alpha, 
        datastore.cv_matrix, 
        datastore.Q_noise, 
        p_data, 
        datastore.v_inertial, 
        datastore.r_meas, 
        datastore.dt)