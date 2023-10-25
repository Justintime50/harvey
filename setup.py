import re

import setuptools


with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

# Inspiration: https://stackoverflow.com/a/7071358/6064135
with open('harvey/_version.py', 'r') as version_file:
    version_groups = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_groups:
        version = version_groups.group(1)
    else:
        raise RuntimeError('Unable to find version string!')

REQUIREMENTS = [
    'docker == 6.1.*',
    'flask == 2.*',
    'python-dotenv == 1.*',
    'pyyaml == 6.*',
    'requests == 2.*',
    'requests_unixsocket == 0.3.*',
    'sentry-sdk == 1.*',
    'slack_sdk == 3.*',
    'sqlitedict == 2.1.*',
    'uwsgi == 2.0.22',  # TODO: Not compatible with Python 3.12+
    'woodchips == 1.*',
]

DEV_REQUIREMENTS = [
    'bandit == 1.7.*',
    'black == 23.*',
    'build == 0.10.*',
    'flake8 == 6.*',
    'isort == 5.*',
    'mypy == 1.5.*',
    'pytest == 7.*',
    'pytest-cov == 4.*',
    'twine == 4.*',
    'types-PyYAML',
    'types-requests',
    'wheel == 0.41.*',
]

setuptools.setup(
    name='harvey-runner',
    version=version,
    description='The lightweight Docker Compose deployment runner.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/harvey',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(
        exclude=[
            'test',
        ]
    ),
    package_data={
        'harvey': [
            'py.typed',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    python_requires='>=3.8, <3.12',
)
