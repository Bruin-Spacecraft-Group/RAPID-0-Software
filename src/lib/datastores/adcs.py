"""
Module of objects and classes which store data pertaining to the current state of the
ADCS system for all tasks to update and use. Readings that have not yet been initialized
are set to `None` throughout this module.
"""

class Datastore:
    """
    """

    def __init__(self):
        self.current_time = None