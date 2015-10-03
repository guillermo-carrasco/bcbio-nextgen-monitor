#!/usr/bin/env python
import glob

from setuptools import setup, find_packages
from pip.req import parse_requirements

try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

setup(name='bcbio_monitor',
      version='0.1',
      description="bcbio-monitor is an extension of bcbio-nextgen to visualize its progress",
      author='Guillermo Carrasco',
      author_email='guille.ch.88@gmail.com',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      entry_points={
        'console_scripts': [
            'bcbio_monitor = bcbio_monitor:main',
        ],
    },
      install_requires=install_requires
)
