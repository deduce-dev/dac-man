#!/usr/bin/env python

from setuptools import setup, find_packages
import os


def get_install_requires():
        # TODO in principle there's a conceptual difference between install_requires and requirements.txt
        # https://packaging.python.org/discussions/install-requires-vs-requirements/
    # so we move dependencies from requirements.txt files to setup.py
    # with open('requirements.txt') as file_requirements:
        # if we want to use requirements.txt as a common basis, we should split/strip "pinned" dependencies
        # (i.e. package==version -> package)
        # install_deps = file_requirements.read().splitlines()

    install_deps = [
        'scandir>=1.5',
        # TODO decide if we should drop support for 2.7
        'six>=1.10.0',
        # NOTE "4.2" caused problems when installing from conda
        # I suspect it might be a matter of differences in package names
        # using "4.2b1" since it seems to be working with both pip and conda
        'PyYAML>=4.2b1',
        'straight.plugin',
        # numpy is required, but only for file-level comparisons
        # (as opposed to directory-level comparisons)
        # should it be considered a core dependency?
        # 'numpy'
    ]

    return install_deps


def get_version():
    _locals = {}

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
      packages=find_packages(exclude=['ez_setup', 'tests', 'plugins']),
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
      install_requires=get_install_requires(),
      entry_points={'console_scripts': ['dacman = dacman.cli:main']},
      data_files=[(os.path.join(dacman_dir, 'config'), ['config/logging.yaml']),
                  (os.path.join(dacman_dir, 'config'), ['config/plugins.yaml'])
                 ]
)
