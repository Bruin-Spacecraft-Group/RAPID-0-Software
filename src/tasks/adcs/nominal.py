"""
Module for ADCS to run nominal operations.
"""

from datastores.adcs import Datastore

import triad as t
from mekf import mekf_update

def get_current_time():
    """
    Placeholder function for getting the current time on satellite
    """

    return 0

def get_sensor_data() -> tuple[float, ...]:
    """
    Polls sun sensor, magnetometer, and model data for sun and geomagnetic data;
    Polls gyro for angular acceleration
    Returns a tuple of 5 floats with the organisation:
    [sun_sensor, sun_model, magnetometer, mag_model, gyro_alpha]
    """

    return [0,0,0,0,0]

def nominal_tasks(datastore: Datastore):
    """
    Highest level nominal loop logic
    """

    datastore.time.current_time = get_current_time()

    diff = datastore.time.current_time - datastore.time.last_cdh_update
    if diff > datastore.time.update_interval:
        update_attitude(datastore)

        datastore.time.last_cdh_update = datastore.time.current_time

def update_attitude(datastore: Datastore):
    """
    Using data from sensors and TRIAD algorithm
    calculates and processes attitude to update datastore values
    """

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
        # IFF sun sensor can be used, use TRIAD algorithm to determine
        # attitude from sensor + model data
        [triad_q, msg] = t.triad_algorithm(s_model, mag_model, s_data, mag_data)

        match msg:
            case t.SUCCESS: # success
                datastore.quaternion = triad_q
            case t.ANTI_PARALLEL: # anti-parallel
                pass
            case t.COLLINEAR: # FAIL : Colinear
                pass
            case t.SINGULAR: # FAIL : Singular (insufficient data)
                pass
            case t.NORM_ERR: # FAIL : Normalisation error (div by 0)
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
