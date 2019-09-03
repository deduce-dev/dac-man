# Installing optional dependencies

Dac-Man has a modular structure, and by default will only install packages that are necessary to its core functionality.

It's possible to install additional dependencies by adding the appropriate labels to the installation command.
For example, to enable analyzing HDF5 and FITS files in an HPC environment:

```sh
pip install git+https://github.com/dghoshal-lbl/dac-man#egg=dacman'[hdf5,fits,hpc]'
```

!!! note
    Using single quotes around the square brackets (like in the code snipped above) might be needed depending on the shell being used.
