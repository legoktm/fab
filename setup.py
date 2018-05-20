#!/usr/bin/env python

from setuptools import setup

setup(name='fab',
      version='2.0.1',
      description='Wrapper around Phabricator API',
      long_description=open('README.rst').read(),
      long_description_content_type='text/x-rst',
      author='Kunal Mehta',
      author_email='legoktm@member.fsf.org',
      license='GPL-3.0-or-later',
      url='https://github.com/legoktm/fab',
      packages=['phabricator'],
      python_requires='>=3.4',
      install_requires=['requests']
      )
