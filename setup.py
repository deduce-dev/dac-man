#!/usr/bin/env python

from setuptools import setup, find_packages
import sys
import os

python_version = sys.version_info

install_deps = []
'''
if python_version[0] == 2:
    if python_version[1] in [6,7]:
        install_deps.append('argparse >= 1.2.1')
install_deps.append('pip>=8.0.1')
install_deps.append('paramiko>=2.1.1')
'''
with open('requirements.txt') as file_requirements:
    install_deps = file_requirements.read().splitlines()

def get_version():
    _locals = {}
    version = f.readline().strip()

    with open("dacman/_version.py") as file_version:
        exec(file_version.read(), None, _locals)

    return _locals['__version__']


dacman_dir = os.path.join(os.getenv('HOME'), '.dacman')
if not os.path.exists(dacman_dir):
    os.makedirs(dacman_dir)

setup(name='dacman',
      version=get_version(),
      description='Data Change Management for Scientific Datasets on HPC systems',
      author='Devarshi Ghoshal',
      author_email='dghoshal@lbl.gov',
      keywords='',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      classifiers=['Development Status :: 1 - Alpha',
                   'Intended Audience :: Science/Research',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering',
                   'License :: OSI Approved :: 3-clause BSD License'
      ],
      install_requires=install_deps,
      entry_points={'console_scripts': ['dacman = dacman.cli:main']},
      data_files=[(os.path.join(dacman_dir, 'config'), ['config/logging.yaml']),
                  ('', ['VERSION'])]
)
