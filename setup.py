from distutils.core import setup
from setuptools import find_packages


setup(
    name='classy-api',
    version='0.0.1',
    description='',
    author='fangorntb',
    author_email='',
    package_dir={
        '': '.',
    },
    packages=find_packages(include=['classy_api', 'classy_api.*']),
    install_requires=[
        'requests',
    ]
)