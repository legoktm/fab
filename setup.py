#!/usr/bin/env python

from setuptools import setup

setup(name='fab',
      version='1.0',
      description='Wrapper around Phabricator API',
      author='Kunal Mehta',
      author_email='legoktm@gmail.com',
      url='https://github.com/legoktm/fab',
      packages=['phabricator'],
      install_requires=['requests']
      )
