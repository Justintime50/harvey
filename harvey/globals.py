# pylint: disable=R0903,C0114
class Global():
    """Contains global configuration for Harvey"""
    DOCKER_VERSION = 'v1.40' # Docker API version
    HARVEY_VERSION = '0.1.0' # Harvey release
    BASE_URL = f'http+unix://%2Fvar%2Frun%2Fdocker.sock/{DOCKER_VERSION}/'
    JSON_HEADERS = {'Content-Type': 'application/json'}
    TAR_HEADERS = {'Content-Type': 'application/tar'}
    ATTACH_HEADERS = {'Content-Type': 'application/vnd.docker.raw-stream'}
    PROJECTS_PATH = 'projects'
    LOGS_PATH = 'logs'
