#!/usr/bin/env python
from setuptools import setup

NAME = 'moth'
DESCRIPTION = 'email-only authentication system'
VERSION = open('VERSION').read().strip()
LONG_DESC = open('README.rst').read()
LICENSE = open('LICENSE').read()

setup(
    name = NAME,
    version = VERSION,
    author = 'Charles Thomas',
    author_email = 'ch@rlesthom.as',
    packages = ['%s' % NAME],
    url = 'https://github.com/charlesthomas/%s' % NAME,
    license = LICENSE,
    description = DESCRIPTION,
    long_description = LONG_DESC,
    test_suite = 'tests',
    install_requires = ["motor >= 0.1"],
)
