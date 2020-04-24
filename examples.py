import json
import requests
import harvey

"""Retrieve a single image"""
# image = harvey.Image.retrieve('harvey/python-test')
# print(image)

"""Retrieve a list of images"""
# images = harvey.Image.all()
# print(json.dumps(images, indent=4))

"""Remove an image"""
# remove_image = harvey.Image.remove('c1d7538e38f74ea6ba43920eaabd27b8')
# print(remove_image)

"""Build an image"""
# image = harvey.Image.build(
#     data = {
#         'language': 'python',
#         'version': '3.7',
#         'project': 'test',
#     },
#     tag = 'harvey/python-test',
# )
# print(image)

"""Retrieve a single container"""
# print(json.dumps(harvey.Container.retrieve('fe3087b2004cac28b820dd48661dd2b4d974293a1b9968a2d8fcc969c0325707'), indent=4))

"""Retrieve a list of container"""
# print(json.dumps(harvey.Container.all(), indent=4))

"""Create a container"""
# container = harvey.Container.create(
#     data = {
#         "Image": "lala", 
#     }
# )
# print(container, "created")

"""Start a container"""
# start = harvey.Container.start('nice_khayyam')
# print(start, "started")

"""Stop a container"""
# container = harvey.Container.stop('fe3087b2004cac28b820dd48661dd2b4d974293a1b9968a2d8fcc969c0325707')
# print(container.name, "stopped")

"""List logs for a container"""
# logs = harvey.Container.logs('089cb9dda0da7c3e0289b6a2cea26837591599ebd531c5a493c4d30548acb38d')
# print(logs)

"""Complete Test"""
# stage_test = harvey.Stage.test(
#     data = {
#         # 'language': 'php',
#         # 'version': 'latest',
#         'project': 'dotfiles',
#     },
# )
# print(stage_test)

"""Build Stage"""
# stage_build = harvey.Stage.build(
#     data = {
#         'project': 'justinpaulhammond.com',
#         # 'dockerfile': 'Dockerfile-dev'
#     },
#     tag = 'justin-test'
# )
# print(stage_build)

"""Deploy Stage"""
# stage_deploy = harvey.Stage.deploy(
#     tag = 'justin-test'
# )
# print(stage_deploy)

"""Full Pipeline"""
# pipeline = harvey.Pipeline.full(
#     data = {
#         'project': 'justinpaulhammond.com',
#         'language': 'php', # for tests
#         'version': 'latest', # for tests
#     },
#     tag = 'justin-test'
# )
# print(pipeline)

"""Webhook"""
# json = open('data.json', 'rb').read()
# hook = requests.post('http://127.0.0.1:5000/git', data=json, headers=Client.JSON_HEADERS)

"""Pull Project"""
# pull = harvey.Webhook.pull(
#     data = {
#         'project': 'justinpaulhammond.com',
#     }
# )

"""Via API"""
# lala = {
#     'data': {
#         'project': 'justinpaulhammond.com',
#         'language': 'php', # for tests
#         'version': 'latest', # for tests
#     },
#     'tag': 'justin-test'
# }


"""Playground"""
with open('./git.json', 'r') as file:
    # json = json.load(file)
    # print(file.read())
    request = requests.post('http://127.0.0.1:5000/webhook', data=file, headers=harvey.Client.JSON_HEADERS)
    print(request)
