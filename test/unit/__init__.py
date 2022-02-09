import os

from harvey.globals import Global


def setup_module():
    """Set up the test suite."""
    if not os.path.exists(Global.STORES_PATH):
        os.mkdir(Global.STORES_PATH)
