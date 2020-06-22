#!/usr/bin/env python

from setuptools import setup, find_packages


def get_install_requires():
    install_deps = [
        'numpy<=1.17',
        'PyYAML>=4.2b1',
        'straight.plugin',
    ]

    return install_deps


def get_extras_require():
    """
    Return optional dependencies in the format required by the
    `extras_require` option.

    These dependencies can then be specified when installing Dac-Man:

    $ git clone <dacman-repo-url> && cd dac-man/
    $ pip install .               # only install core dependencies
    $ pip install .[fits]         # install also dependencies necessary for
                                    FITS files
    $ pip install .[fits,h5,hpc]  # install multiple optional dependencies
    """
    d = {}

    d['fits'] = ['astropy']
    d['edf'] = ['fabio']
    d['h5'] = ['h5py']
    d['csv'] = ['pandas']

    d['hpc'] = ['mpi4py']

    return d


def get_version():
    _locals = {}

    with open("dacman/_version.py") as file_version:
        exec(file_version.read(), None, _locals)

    return _locals['__version__']


setup(name='dacman',
      version=get_version(),
      description=('Data Change Management for Scientific Datasets '
                   'on HPC systems'),
      author='Devarshi Ghoshal',
      author_email='dghoshal@lbl.gov',
      keywords='',
      classifiers=['Development Status :: 1 - Alpha',
                   'Intended Audience :: Science/Research',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering',
                   'License :: OSI Approved :: 3-clause BSD License'],
      packages=find_packages(exclude=['ez_setup', 'tests']),
      include_package_data=True,
      package_data={'dacman': ['config/*.yaml']},
      zip_safe=False,
      install_requires=get_install_requires(),
      extras_require=get_extras_require(),
      entry_points={'console_scripts': ['dacman = dacman.cli:main']})
