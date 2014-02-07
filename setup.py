#!/usr/bin/env python
from setuptools import setup

NAME = 'moth'
DESCRIPTION = 'token system using MongoDB'
VERSION = open('VERSION').read().strip()
LONG_DESC = open('README.rst').read()
LICENSE = open('LICENSE').read()

setup(
    name=NAME,
    version=VERSION,
    author='Charles Thomas',
    author_email='ch@rlesthom.as',
    packages=['%s' % NAME],
    url='https://%s.readthedocs.org' % NAME,
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    test_suite='tests',
    install_requires=["motor >= 0.1"],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Communications :: Email',
                 'Topic :: Database',
                 'Topic :: Internet :: WWW/HTTP :: Session',
                 'Topic :: Security',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)
