# Default Plug-in

## Dac-Man records

The default plug-in in Dac-Man uses a data astraction called Dac-Man records
to compare changes for different file formats and data types.
Dac-Man records transform the header and data of a file into an array.
The records from two files are then compared using a linear algorithm.

## Adaptors

The default plug-in uses several adaptors to transform data
from different file formats into Dac-Man records.
Currently, the plug-in uses adaptors for the following file formats:

| File type | Description |
| --- | --- |
| `h5` | HDF file format |
| `fits` | Image file format consisting of *n*-dimensional arrays or tables |
| `edf` | Time-series data format |
| `tif` | High-quality graphics image format |

## Requirements

To use the default plug-in, users need to install the required dependencies.
The list of packages required for each file type is as follows:

| File type | Package name | URL |
| --- | --- | --- |
| `h5` | `h5py` | [docs.h5py.org](http://docs.h5py.org/en/latest/index.html) |
| `fits` | `astropy` | [astropy.org](https://www.astropy.org/) |
| `edf` | `fabio` | [fabio.readthedocs.io](https://fabio.readthedocs.io/en/latest/) |
| `tif` | `fabio` |  |

!!! tip
    Dependencies can be also installed directly during Dac-Man's installation.
    For more information refer to the [Installation](../../install/dependencies) section.
