"""
Module for ADCS to run nominal operations.
"""

from quaternion import Quaternion
import ulab.numpy as np

from datastores.adcs import Datastore

from triad import triad_algorithm
from mekf import mekf_update

def get_current_time():
    pass

def get_sensor_data() -> tuple[float, float, float, float]:
    """
    Polls sun sensor, magnetometer, and model data for sun and geomagnetic data.
    Returns a tuple of 4 floats with the organisation:
    [sun_sensor, sun_model, magnetometer, mag_model]
    """
    pass

def get_gyro_data():
    pass

def nominal_tasks(datastore: Datastore):
    """
    Highest level nominal loop logic
    """
    
    datastore.current_time = get_current_time()
    
    if (datastore.current_time - datastore.last_cdh_update > datastore.update_interval):
        update_attitude(datastore)

        datastore.last_cdh_update = datastore.current_time

def update_attitude(datastore: Datastore):
    # Placeholders for sun sensor data, sun model data, magnetometer data, and geomagnetic model data
    [s_data, s_model,
     mag_data, mag_model] = get_sensor_data()
 
    # use TRIAD algorithm to determine attitude from sensor + model data
    [triad_q, msg] = triad_algorithm(s_model, mag_model, s_data, mag_data)

    # error handling/checking message
    match msg:
        case 0: # success
            gyro_data = get_gyro_data()
            datastore.quaternion = triad_q

            # I'm going to spend a little more time figuring out what's happening in this function - Aaron
            mekf_update(datastore.quaternion, gyro_data) # gyro_data.alpha
        case _: # catch None or weird case
            pass