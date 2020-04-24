import requests_unixsocket

class Client():
    VERSION = 'v1.40'
    BASE_URL = f'http+unix://%2Fvar%2Frun%2Fdocker.sock/{VERSION}/'
    JSON_HEADERS = {'Content-Type': 'application/json'}
    TAR_HEADERS = {'Content-Type': 'application/tar'}
    ATTACH_HEADERS = {'Content-Type': 'application/vnd.docker.raw-stream'}
