from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup (
    name='ays',
    version='0.9',
    description='Python client for the AYS RESTful API',
    long_description=long_description,
    url='https://github.com/jumpscale/ays9',
    author='Yves Kerwyn',
    author_email='yves@gig.tech',
    license='Apache 2.0',
    namespaces=['ays'],
    packages=find_packages(),
    install_requires=[],
)
