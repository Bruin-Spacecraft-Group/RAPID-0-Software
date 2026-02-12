"""
Module holding the main loop of the ADCS task structure
"""

import nominal as nm
import detumble as dtmb
import point_to_sun as pts
import point_to_earth as pte

from datastores.adcs import Datastore


async def main_adcs_loop(ds: Datastore):
    """
    ADCS Loop to be run as an asynchronous task on breakout board
    """

    while True:
        adcs_mode = ds.mode
        if adcs_mode == ds.DETUMBLE:
            dtmb.detumble(ds)
        elif adcs_mode == ds.POINT_TO_SUN:
            pts.point_to_sun(ds)
        elif adcs_mode == ds.POINT_TO_EARTH:
            pte.point_to_earth(ds)
        elif adcs_mode == ds.NOMINAL_PROCESSES:
            nm.nominal_tasks(ds)
        else:
            return 1
