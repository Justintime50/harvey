import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'flask >= 1.1.2',
    'requests >= 2.24.0',
    'requests_unixsocket >= 0.2.0',
    'slackclient >= 2.7.2',
    'python-dotenv >= 0.10.0'
]

setuptools.setup(
    name='harvey-ci',
    version='0.8.2',
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
        'dev': [
            'pytest >= 6.0.0',
            'pytest-cov >= 2.10.0',
            'coveralls >= 2.1.2',
            'flake8 >= 3.8.0',
            'mock >= 4.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'harvey-ci=harvey.app:main'
        ]
    },
    python_requires='>=3.6',
)
