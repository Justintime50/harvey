import os

from harvey.config import Config


def setup_module():
    """Set up the test suite."""
    if not os.path.exists(Config.stores_path):
        os.makedirs(Config.stores_path)
