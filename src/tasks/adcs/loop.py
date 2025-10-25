from datastores.adcs import datastore as ds
import nominal.py as nominal
import detumble.py as detumble
import point_to_sun.py as point_to_sun
import point_to_earth.py as point_to_earth


def main_loop():
    ADCS_mode = ds.mode
    if ADCS_mode == ds.DETUMBLE:
        detumble.detumble()
    elif ADCS_mode == ds.POINT_TO_SUN:
        point_to_sun.point_to_sun()
    elif ADCS_mode == ds.POINT_TO_EARTH:
        point_to_earth.point_to_earth()
    elif ADCS_mode == ds.NOMINAL_PROCESSES:
        nominal.nominal_tasks(ds)
    else:
        return 1
