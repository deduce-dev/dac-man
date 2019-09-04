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
* It identifies changes between non-co-located datasets without the need      for transferring the data, i.e., datasets need not be moved to a common location for comparison.

Documentation
-------------

Installation and usage instructions,
as well as commented examples illustrating Dac-Man's features,
are available on [Dac-Man's documentation website](https://dst.lbl.gov/projects/deduce/dac-man/).

Contribute
----------

* Issue Tracker: <https://github.com/dghoshal-lbl/dac-man/issues>
* Source Code: <https://github.com/dghoshal-lbl/dac-man>

Support
-------

If you have any issues, please contact us at: dac-man@lbl.gov

License
-------

Dac-Man is licensed under the BSD 3-Clause license.
