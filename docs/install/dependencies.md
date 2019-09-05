# Installing additional dependencies

Dac-Man has a modular structure, and by default will only install packages that are necessary to its core functionality.

It's possible to install additional dependencies by updating Dac-Man's Conda environment
using environment files in the `environment` directory of the source code repository.

!!! tip
    For more information on individual dependencies, refer to the contents of each environment file.

## Installing dependencies for all built-in plug-ins

To update Dac-Man's environment to enable all built-in plug-ins,
from the root of the local copy of the Dac-Man source code repository,
run:

```sh
conda env update --name dacman-env --file environment/builtin-plugins.yml
```

## Installing dependencies for running Dac-Man with MPI

The `mpi4py` package is required to use Dac-Man with MPI.

To update Dac-Man's environment, run this command from the root of the local copy
of the Dac-Man's source code repository:

```sh
conda env update --name dacman-env --file environment/mpi.yml
```

!!! important
    Different computing environments might have specific requirements for interfacing user applications with MPI, e.g. using custom versions of MPI libraries. This is especially true for HPC systems. In this case, refer to the system's own documentation to find out how to enable MPI.
