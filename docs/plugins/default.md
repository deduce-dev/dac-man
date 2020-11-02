# Default Plug-in

The Dac-Man default plug-in compares file contents for several file formats through an intermediate array-based representation.

## Key concepts

### Dac-Man records

The Dac-Man default plug-in uses a data abstraction called Dac-Man records
to compare changes for different file formats and data types.
Dac-Man records transform the header and data of a file into an array.
The records from two files are then compared using a linear algorithm.

### Adaptors

The default plug-in uses several adaptors to transform data
from different file formats into Dac-Man records.
Currently, the plug-in uses adaptors for the following file formats:

| File type | Description |
| --- | --- |
| `h5` | HDF file format |
| `fits` | Image file format consisting of *n*-dimensional arrays or tables |
| `edf` | Time-series data format |
| `tif` | High-quality graphics image format |

## Usage

### Requirements

!!! tip
    These [instructions](../../install/dependencies) describe how to install
    dependencies for all of Dac-Man's included plug-ins in a single step.

This plug-in requires additional packages, depending on the exact file type
that will be analyzed, as described in the following table:

| File type | Package name | URL |
| --- | --- | --- |
| `h5` | `h5py` | [docs.h5py.org](https://docs.h5py.org/en/latest/index.html) |
| `fits` | `astropy` | [astropy.org](https://www.astropy.org/) |
| `edf` | `fabio` | [fabio.readthedocs.io](https://fabio.readthedocs.io/en/latest/) |
| `tif` | `fabio` | [fabio.readthedocs.io](https://fabio.readthedocs.io/en/latest/) |
