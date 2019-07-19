# HDF5 Plug-in

A Dac-man plug-in to compare HDF5 files, using information from metadata collected from the contained Objects.

## Dependencies

The `hdf5` plug-in requires the `h5py` Python package to operate.

## Usage

### From the command line (standalone mode)

After installing Dac-Man, run:

```sh
python -m dacman.plugins.hdf5 A.h5 B.h5
```

where `A.h5` and `B.h5` are the two HDF5 files to compare.

Use the `--help` flag for a complete list of command-line options:

```sh
python -m dacman.plugins.hdf5 --help
```
