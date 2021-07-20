import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'flask == 1.*',  # TODO: bump to v2 after thorough testing
    'requests == 2.*',
    'requests_unixsocket == 0.2.*',
    'slackclient == 2.*',
    'python-dotenv == 0.17.*'
]

DEV_REQUIREMENTS = [
    'coveralls == 3.*',
    'flake8',
    'mock == 4.*',
    'pytest == 6.*',
    'pytest-cov == 2.*',
]

setuptools.setup(
    name='harvey-ci',
    version='0.11.0',
    description='Your personal CI/CD and Docker orchestration platform.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/harvey',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS
    },
    entry_points={
        'console_scripts': [
            'harvey-ci=harvey.app:main'
        ]
    },
    python_requires='>=3.6',
)
