#!/usr/bin/env python
from distutils.core import setup
from os.path import dirname, join

VERSION = open( join( dirname( __file__ ), 'VERSION' ) ).read()
DESCRIPTION = 'Authentication made easy'

setup(
    name = 'moth',
    version = VERSION,
    description = DESCRIPTION,
    author = 'Charles Thomas',
    author_email = 'ch@rlesthom.as',
    url = 'http://bitbucket.org/charlesthomas/moth',
)
