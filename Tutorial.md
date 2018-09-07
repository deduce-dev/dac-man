******************************************************************************
Dac-Man Tutorial: A guide to using the command-line tool in Dac-Man.

******************************************************************************

## Comparing two directories of dataset
To detect changes between two directories `dir1` and `dir2`, users can simply run:

        dacman diff dir1 dir2

## Comparing two data files
Users can retrieve changes between any two files similar to two directories:

       dacman diff dir1/myfile dir2/myfile

## Retriving detailed data changes between two files
Users can retrieve detailed data changes between any two files as:

       dacman diff dir1/myfile dir2/myfile --datachange

## Comparing datasets with read-only access
If the data directories have read-only access, then users can stage the metadata and indexes
in a user-defined location using the `-s` option.
 
       dacman index datadir -s staging_dir 

## Comparing datasets at two different sites
In order to compare datasets at two different sites, users can create indexes in a user-defined
location (as shown in the previous step), and copy the staged indexes to a common location,
`shared_index_location`. Users can then retrieve the changes as:

       dacman diff local_dir remote_dir -s shared_index_location

## Using Dac-Man @ NERSC
In order to use Dac-Man at NERSC, users need to write a batch script and
submit the script through a batch scheduler:

      #SBATCH -J example
      #SBATCH -t 00:30:00
      #SBATCH -N 8
      #SBATCH -q myqueue
      
      mpiexec -n 256 dacman diff /old/data /new/data -e mpi


# Using a custom data change plug-in
Users can use a custom script (e.g., `myscript`) for calculating data changes between two files as:

       dacman diff dir1/myfile dir2/myfile -a myscript


