import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'docker == 5.0.*',
    'flask == 2.*',
    'gunicorn == 20.1.*',
    'python-dotenv == 0.19.*',
    'requests == 2.*',
    'requests_unixsocket == 0.2.*',
    'slackclient == 2.*',
    'woodchips == 0.2.*',
]

DEV_REQUIREMENTS = [
    'black',
    'coveralls == 3.*',
    'flake8',
    'isort',
    'mypy',
    'pytest == 6.*',
    'pytest-cov == 2.*',
    'types-requests',
]

setuptools.setup(
    name='harvey-ci',
    version='0.15.0',
    description='The lightweight Docker Compose deployment platform.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/harvey',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(),
    package_data={'harvey': ['py.typed']},
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
        'console_scripts': ['harvey-ci=harvey.app:main'],
    },
    python_requires='>=3.7, <4',
)
