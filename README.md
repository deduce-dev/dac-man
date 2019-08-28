******************************************************************************
Dac-Man: A framework to track, compare and analyze large scientific data changes 
******************************************************************************

Dac-Man is a framework to enable tracking, comparing and analyzing changes
in large scientific data sets.

You can find the changes between two datasets using the command-line utility:

        dacman diff <old datapath> <new datapath>

Features
--------

Dac-Man is much more powerful than a simple diff utility.

* It is extremely fast: it can retrieve changes from terabytes of data within seconds.
* It can be used on desktops, as well as on large supercomputers.
* It allows users to associate user-defined metadata for any dataset.
* It is capable of identifying both file and data level changes.
* It allows users to plugin their own scripts for richer change analysis.
* It identifies changes between non-co-located datasets without the need for transferring
the data, i.e., datasets need not be moved to a common location for comparison.

Installation
------------

Dac-Man is developed in Python, with the following minimal requirements:

* Python (>= 3.6)
* pip (>= 9.0)

For HPC support, you need:

* numpy   : Python library for operations on large, multi-dimensional arrays
* mpi4py  : Python MPI bindings

To install Dac-Man, run the setup script:

        python setup.py install

Test
-----

The `examples/` directory contains a simple example and related data to test
Dac-Man command-line. To test, run the following commands:

        cd examples
        ./scripts/simple.sh

Running the test suite
----------------------

Dac-man's test suite can be found in the `tests/` directory.
The [Tox](https://tox.readthedocs.io/en/latest/) utility is used to run the test suite automatically over multiple Python versions.

To run the test suite using Tox, from the root of the repository:

```sh
pip install tox
tox
```

Depending on which Python interpreters are available in the environment, some tests might fail.
The [tox-conda](https://github.com/tox-dev/tox-conda) plugin allows Tox to use Conda to install and manage packages and environments:

```sh
pip install tox tox-conda
tox
```

Contribute
----------

- Issue Tracker: https://github.com/dghoshal-lbl/dac-man/issues
- Source Code: https://github.com/dghoshal-lbl/dac-man

Support
-------

If you have any issues, please contact us at: dac-man@lbl.gov

License
-------

Dac-Man is licensed under the BSD 3-Clause license.