#!/usr/local/bin/python3.4

"""
## Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## ALL RIGHTS RESERVED.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## Neither the name of the SONATA-NFV, 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## nor the names of its contributors may be used to endorse or promote
## products derived from this software without specific prior written
## permission.
##
## This work has been performed in the framework of the SONATA project,
## funded by the European Commission under Grant number 671517 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the SONATA
## partner consortium (www.sonata-nfv.eu).
##
## This work has been performed in the framework of the 5GTANGO project,
## funded by the European Commission under Grant number 761493 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the 5GTANGO
## partner consortium (www.5gtango.eu).
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sonata_adapter',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='v0.1',

    description='5GTANGO resisto adapter',
    long_description=long_description,

    # The project's main homepage.
    #url='https://github.com/sonata-nfv/tng-resisto-api/tree/master/',

    # Author details
    author='Carlos Marques',
    #author_email='carlos-martins-marques@alticelabs.com',

    # Choose your license
    license='Apache 2.0',

    # What does your project relate to?
    keywords='Multi domain',

    packages=find_packages(),
    install_requires=['Flask==1.1.1', 'flask-restful==0.3.7', 'python-dateutil==2.8.0', 'requests==2.22.0', 'xmlrunner==1.7.7', 'pika==1.1.0', 'coloredlogs==10.0', 'MarkupSafe==1.1.1', 'jinja2==2.10.3', 'itsdangerous==1.1.0'],

    #aniso8601 (8.0.0)
    #certifi (2019.11.28)
    #chardet (3.0.4)
    #Click (7.0)
    #coloredlogs (10.0)
    #Flask (1.1.1)
    #Flask-RESTful (0.3.7)
    #humanfriendly (4.18)
    #idna (2.8)
    #itsdangerous (1.1.0)
    #Jinja2 (2.10.3)
    #MarkupSafe (1.1.1)
    #pika (1.1.0)
    #pip (9.0.1)
    #python-dateutil (0.0.0)
    #pytz (2019.3)
    #requests (2.22.0)
    #setuptools (36.6.0)
    #six (1.13.0)
    #tng-slice-mngr (0.1)
    #urllib3 (1.25.7)
    #Werkzeug (0.16.0)
    #wheel (0.30.0)
    #xmlrunner (1.7.7)

    #setup_requires=['pytest-runner'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': ['sonata_adapter=sonata_adapter.__main__:main'],
    #},
)
