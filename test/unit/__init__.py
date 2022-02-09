import os

from harvey.globals import Global


def setup_module():
    stores_path = Global.STORES_PATH
    if not os.path.exists(stores_path):
        os.mkdir(stores_path)
