#!/usr/bin/env python

from setuptools import setup
from pip.req import parse_requirements

install_requires = parse_requirements('requirements.txt')

setup(name='bcbio-nextgen-monitor',
      version='0.1',
      description="bcbio-nextgen-monitor is an extension of bcbio-nextgen to visualize its progress",
      author='Guillermo Carrasco',
      author_email='guille.ch.88@gmail.com',
      install_requires = [str(r.req) for r in install_requires]
)
