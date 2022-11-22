import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'docker == 6.0.*',
    'flask == 2.*',
    'python-dotenv == 0.20.*',
    'pyyaml == 6.*',
    'requests == 2.*',
    'requests_unixsocket == 0.3.*',
    'sentry-sdk == 1.7.*',
    'slackclient == 2.*',
    'sqlitedict == 2.0.*',
    'uwsgi == 2.0.21',
    'woodchips == 0.2.*',
]

DEV_REQUIREMENTS = [
    'bandit == 1.7.*',
    'black == 22.*',
    'build == 0.8.*',
    'flake8 == 4.*',
    'isort == 5.*',
    'mypy == 0.961',
    'pytest == 7.*',
    'pytest-cov == 4.*',
    'twine == 4.*',
    'types-PyYAML',
    'types-requests',
    'wheel == 0.37.*',
]

setuptools.setup(
    name='harvey-cd',
    version='0.21.0',
    description='The lightweight Docker Compose deployment platform.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/harvey',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(
        exclude=[
            'examples',
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
    entry_points={
        'console_scripts': ['harvey=harvey.app:main'],
    },
    python_requires='>=3.7, <4',
)
