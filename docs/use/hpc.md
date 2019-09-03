# Using Dac-Man on HPC Clusters

## Using MPI

Dac-Man allows you to parallelize `index` and `diff` steps.
To parallelize on HPC clusters, you need to enable the MPI support
by using the appropriate flags:

```sh
dacman index ... -m mpi
dacman diff ... -e mpi
```

To distribute the tasks to multiple workers, you need to use `mpirun` or `mpiexec`.
For example, running Dac-Man on an HPC cluster with 8 nodes and 32 cores per node,
you can use:

```sh
mpiexec -n 256 dacman index ... -m mpi
mpiexec -n 256 dacman diff ... -e mpi
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

mpiexec -n 256 dacman diff /old/data /new/data -e mpi
```

The script can then be submitted to the batch scheduler as:

```sh
sbatch hpcEx.batch
```
