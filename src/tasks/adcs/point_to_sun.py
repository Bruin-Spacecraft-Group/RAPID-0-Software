"""
Module to handle point_to_sun procedure in ADCS
"""

from datastores.adcs import Datastore


def point_to_sun(datastore: Datastore):
    """
    Empty function declaration to be used by loop.py in larger ADCS loop
    """

    print(datastore.mode + 'Mode')
