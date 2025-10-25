from datastores.adcs import datastore as ds


def detumble():
    pass


def point_to_sun():
    pass


def point_to_earth():
    pass


def nominal_processes():
    pass


def main():
    ADCS_mode = ds.mode
    if ADCS_mode == 1:
        detumble()
    elif ADCS_mode == 2:
        point_to_sun()
    elif ADCS_mode == 3:
        point_to_earth()
    elif ADCS_mode == 4:
        nominal_processes()
    else:
        return 1
