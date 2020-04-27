# pylint: disable=R0903,C0114
class Global():
    """Contains all the data to craft the requests client"""
    VERSION = 'v1.40' # Docker API version
    BASE_URL = f'http+unix://%2Fvar%2Frun%2Fdocker.sock/{VERSION}/'
    JSON_HEADERS = {'Content-Type': 'application/json'}
    TAR_HEADERS = {'Content-Type': 'application/tar'}
    ATTACH_HEADERS = {'Content-Type': 'application/vnd.docker.raw-stream'}
    PROJECTS_PATH = 'docker/projects/'
    TEST_PATH = 'docker/'
