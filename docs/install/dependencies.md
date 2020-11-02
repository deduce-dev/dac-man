# Installing plug-in dependencies

Dac-Man has a modular structure, and by default will only install packages that are necessary to its core functionality.
To enable Dac-Man's included plug-ins, the required additional dependencies must be installed.

It is possible to install additional dependencies by updating Dac-Man's environment
using files in the `dependencies/` directory of the source code repository.

## Installing dependencies for all included plug-ins

### Using Conda

If Dac-Man was installed using Conda,
run this command from the root of the local copy of the Dac-Man source code repository
to update Dac-Man's environment and enable all included plug-ins:

```sh
conda env update --name dacman-env --file dependencies/conda/builtin-plugins.yml
```

### Using Pip

If Dac-Man was installed using Pip,
activate Dac-Man's environment, and then run the following command instead:

```sh
pip install --requirement dependencies/pip/builtin-plugins.txt
```

## Built-in plug-ins dependencies

More information about the individual dependencies required by the included
plug-ins are given in the following table.

| Package name | Documentation URL | Required by plug-in | Required for |
|: --- |: --- :| --- | -- |
| `h5py` | [Link](https://docs.h5py.org/en/latest/index.html) | Default, HDF5 | Reading `.h5` files |
| `astropy` | [Link](https://docs.astropy.org/en/stable/) | Default | Reading `.fits` files |
| `fabio` | [Link](https://fabio.readthedocs.io/en/latest/) | Default | Reading `.edf` and `.tif` files |
| `pandas` | [Link](https://pandas.pydata.org/pandas-docs/stable/) | CSV, Excel | Reading `.csv`/`.xls*` files, data processing |
| `xlrd` | [Link](https://xlrd.readthedocs.io/en/latest/) | Excel | Reading `.xls*` files (through `pandas`), Excel utility functions |
