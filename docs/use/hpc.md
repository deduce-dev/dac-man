# Using Dac-Man on HPC Clusters

## Requirements

The `mpi4py` is required to enable running Dac-Man with MPI.
Installation steps and additional information
on how to install Dac-Man's MPI dependencies are given in the following.

### Installing dependencies for running Dac-Man with MPI

The `mpi4py` package is required to use Dac-Man with MPI.

To update Dac-Man's environment, run this command from the root of the local copy
of the Dac-Man's source code repository:

```sh
conda env update --name dacman-env --file dependencies/conda/mpi.yml
```

!!! important
    Different computing environments might have specific requirements for interfacing user applications with MPI, e.g. using custom versions of MPI libraries. This is especially true for HPC systems. In this case, refer to the system's own documentation to find out how to enable MPI.

## Using MPI

Dac-Man allows you to parallelize the following steps:

- `index`
- `diff` with the `--datachange` option

To parallelize on HPC clusters, you need to enable the MPI support
by using the appropriate flags:

```sh
dacman index ... -m mpi
dacman diff ... -e mpi --datachange
```

To distribute the tasks to multiple workers,
you need to use the MPI executable appropriate for the system in use,
e.g. `srun`, `mpiexec`, `mpirun`, etc.

For example, to run Dac-Man on an HPC cluster with 8 nodes and 32 cores per node,
where the MPI executable is `srun`,
you can use:

```sh
srun -n 256 dacman index ... -m mpi
srun -n 256 dacman diff ... -e mpi --datachange
```

## Batch Script

To submit a batch job to a cluster,
you need to include the Dac-Man command in your job script.
The example below shows a batch script (`hpcEx.batch`) for the Slurm scheduler.

```sh
# !/bin/bash

#SBATCH -J example
#SBATCH -t 00:30:00
#SBATCH -N 8
#SBATCH -q myqueue

srun -n 256 dacman diff /old/data /new/data -e mpi --datachange
```

The script can then be submitted to the batch scheduler as:

```sh
sbatch hpcEx.batch
```

---

## Using Dac-Man on NERSC

This sections provides information on how to run Dac-Man at scale on the Cori HPC cluster at NERSC.

### Installation

#### Enabling Conda

The Conda package manager is already installed at NERSC.
To enable it, from one of Cori's login nodes,
load one of the Anaconda Python modules as described [here](https://docs.nersc.gov/programming/high-level-environments/python/#anaconda-python):

```sh
module load python/3.7-anaconda-2019.07
```

#### Installing Dac-Man

Then, follow the same steps to install Dac-Man using Conda as illustrated in the [*Installing Dac-Man*](../../install/) section,
including installing additional [plug-in dependencies](../../dependencies/) as needed:

```sh
git clone https://github.com/dghoshal-lbl/dac-man
cd dac-man
conda env create --file environment.yml
# optional - install dependencies for built-in plug-ins
conda env update --name dacman-env --file dependencies/conda/builtin-plugins.yml
```

#### Enable MPI

The installation method for MPI dependencies described above will not work on Cori,
since the package versions installed via Pip or Conda are not compatible with the MPI libraries supported on Cori.

To enable MPI on Cori, the `mpi4py` package must be built manually.
To do so, first activate the Dac-Man Conda environment:

```sh
conda activate dacman-env
```

Then, follow the steps described in [this section](https://docs.nersc.gov/programming/high-level-environments/python/mpi4py/#mpi4py-in-your-custom-conda-environment) of the NERSC documentation
to download, build, and install the `mpi4py` package.

### Running a test job

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
