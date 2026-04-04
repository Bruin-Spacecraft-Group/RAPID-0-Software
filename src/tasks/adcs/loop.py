"""
Module holding the main loop of the ADCS task structure
"""

import nominal as nm
import detumble as dtmb
import point_to_sun as pts
import point_to_earth as pte

import datastore as ds


async def main_adcs_loop(datastore: ds.Datastore):
    """
    ADCS Loop to be run as an asynchronous task on breakout board
    """

    while True:
        adcs_mode = datastore.mode
        if adcs_mode == datastore.DETUMBLE:
            dtmb.detumble(datastore)
        elif adcs_mode == datastore.POINT_TO_SUN:
            pts.point_to_sun(datastore)
        elif adcs_mode == datastore.POINT_TO_EARTH:
            pte.point_to_earth(datastore)
        elif adcs_mode == datastore.NOMINAL_PROCESSES:
            nm.nominal_tasks(datastore)
        else:
            return 1
