"""
Module for handling the ADCS function point_to_earth
"""

from datastores.adcs import Datastore


def point_to_earth(datastore: Datastore):
    """
    Empty function declaration to be used by loop.py in larger ADCS loop
    """

    print(datastore.mode + 'Mode')
