# Using Dac-Man at NERSC

This sections provides information on how to run Dac-Man at scale on the Cori HPC cluster at NERSC.

## Installation

### Enabling Conda

The Conda package manager is already installed at NERSC.
To enable it, from one of Cori's login nodes,
load one of the Anaconda Python modules as described [here](https://docs.nersc.gov/programming/high-level-environments/python/#anaconda-python):

```sh
module load python/3.7-anaconda-2019.07
```

### Installing Dac-Man

Then, follow the same steps to install Dac-Man using Conda as illustrated in the [*Installing Dac-Man*](../../install/) section,
including installing additional [plug-in dependencies](../../install/dependencies/) as needed:

```sh
git clone https://github.com/dghoshal-lbl/dac-man
cd dac-man
conda env create --file environment.yml
# optional - install dependencies for built-in plug-ins
conda env update --name dacman-env --file dependencies/conda/builtin-plugins.yml
```

### Enable MPI

The installation method for MPI dependencies described above will not work on Cori,
since the package versions installed via Pip or Conda are not compatible with the MPI libraries supported on Cori.

To enable MPI on Cori, the `mpi4py` package must be built manually.
To do so, first activate the Dac-Man Conda environment:

```sh
conda activate dacman-env
```

Then, follow the steps described in [this section](https://docs.nersc.gov/programming/high-level-environments/python/mpi4py/#mpi4py-in-your-custom-conda-environment) of the NERSC documentation
to download, build, and install the `mpi4py` package.

## Running a test job

After the installation is finished,
test Dac-Man on one of Cori compute nodes using an interactive session.

To access a node in an interactive session, run:

```sh
salloc -N 1 -C haswell -q interactive -t 30:00
```

Finally, once inside the interactive compute node session,
invoke `dacman` on any two test data directories.
On Cori, the MPI executable is `srun`:

```sh
srun -n 32 dacman diff <dir-1> <dir-2> -e mpi --datachange
```

!!! important
    Make sure that you run this command in a Cori compute node, as opposed to a login node. Running MPI on login nodes is discouraged at NERSC, and the above command might fail if run on a login node.
