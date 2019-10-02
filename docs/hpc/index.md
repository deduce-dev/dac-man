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
