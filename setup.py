from setuptools import find_packages, setup
from os import path
from codecs import open

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='configuration_builder',
    packages=find_packages(include=['configuration_builder']),
    version='0.1.0',
    description='Configuration builder allow make app configuration',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Klabukov Erik',
    license='MIT'
)
