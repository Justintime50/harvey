import os

from harvey.config import Config


def setup_module():
    """Set up the test suite."""
    if not os.path.exists(Config.database_path):
        os.makedirs(Config.database_path)
