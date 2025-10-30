"""
Module for handling the Detumble procedure for ADCS
"""

from datastores.adcs import Datastore


def detumble(datastore: Datastore):
    """
    Empty function declaration to be used by loop.py in larger ADCS loop
    """

    print(datastore.mode + 'Mode')
