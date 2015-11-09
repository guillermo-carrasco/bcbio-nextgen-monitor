#!/usr/bin/env python
from setuptools import setup, find_packages

try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

setup(name='bcbio_monitor',
      # For versioning: http://semver.org/
      version='0.2.0',
      description="bcbio-monitor is an extension of bcbio-nextgen to visualize its progress",
      author='Guillermo Carrasco',
      author_email='guille.ch.88@gmail.com',
      url='https://github.com/guillermo-carrasco/bcbio-nextgen-monitor',
      packages=find_packages(),
      include_package_data=True,
      keywords=['bcbio', 'bcbio-nextgen', 'bioinformatics', 'genomics'],
      zip_safe=True,
      entry_points={
        'console_scripts': [
            'bcbio_monitor = bcbio_monitor:main',
        ],
    },
      install_requires=install_requires
)
