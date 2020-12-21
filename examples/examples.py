import requests  # noqa
import json  # noqa
import harvey


# """Retrieve a single image"""
# image = harvey.Image.retrieve_image('harvey/python-test')
# print(image)

# """Retrieve a list of images"""
# images = harvey.Image.retrieve_all_images()
# print(json.dumps(images, indent=4))

# """Remove an image"""
# remove_image = harvey.Image.remove_image('c1d7538e38f74ea6ba43920eaabd27b8')
# print(remove_image)

# """Build an image"""
# image = harvey.build_image(
#     config={
#         'language': 'python',
#         'version': '3.7',
#     },
# )
# print(image)

# """Retrieve a single container"""
# print(json.dumps(harvey.Container.inspect_container(
#     'fe3087b2004cac28b820dd48661dd2b4d974293a1b9968a2d8fcc969c0325707'
# ), indent=4))

# """Retrieve a list of container"""
# print(json.dumps(harvey.Container.list_containers(), indent=4))

# """Create a container"""
# container = harvey.Container.create_container(
#     config={
#         "Image": "lala",
#     }
# )
# print(container, "created")

# """Start a container"""
# start = harvey.Container.start_container('nice_khayyam')
# print(start, "started")

# """Stop a container"""
# container = harvey.Container.stop_container(
#     'fe3087b2004cac28b820dd48661dd2b4d974293a1b9968a2d8fcc969c0325707')
# print(container.name, "stopped")

# """List logs for a container"""
# logs = harvey.Container.inspect_container_logs(
#     '089cb9dda0da7c3e0289b6a2cea26837591599ebd531c5a493c4d30548acb38d'
# )
# print(logs)

# """Complete Test"""
# stage_test = harvey.Stage.test(
#     config={
#         'language': 'php',
#         'version': 'latest',
#     },
# )
# print(stage_test)

# """Build Stage"""
# stage_build = harvey.Stage.build()
# print(stage_build)

# """Deploy Stage"""
# stage_deploy = harvey.Stage.deploy()
# print(stage_deploy)

# """Full Pipeline"""
# pipeline = harvey.Pipeline.full(
#     config={
#         'language': 'php',  # for tests
#         'version': 'latest',  # for tests
#     },
# )
# print(pipeline)

# """Pull Project"""
# pull = harvey.Webhook.pull(
#     data={
#         'project': 'justinpaulhammond.com',
#     }
# )

"""API Entrypoint (Webhook)"""
with open('examples/git_webhook.json', 'r') as file:
    data = json.load(file)
    request = requests.post(
        'http://127.0.0.1:5000/pipelines/start',
        json=data,
        headers=harvey.Global.JSON_HEADERS
    )
    print(request.json())

# """Retrieve a Pipeline by ID"""
# request = requests.get(
#     'http://127.0.0.1:5000/pipelines/f599cde2f2a0ad562bb7982328fe0aeee9d22b1c',
#     headers=harvey.Global.JSON_HEADERS
# )
# print(request.text)

# """Retrieve all pipelines"""
# request = requests.get(
#     'http://127.0.0.1:5000/pipelines', headers=harvey.Global.JSON_HEADERS)
# print(request.text)
