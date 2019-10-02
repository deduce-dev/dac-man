# Dac-Man Quick Start Guide

This document will get you started using the Dac-Man data change tool on your personal computer.
This guide will help you use the Dac-Man tool to compare two versions of a sample dataset.
Having completed this guide you will be ready to use Dac-Man to compare your own datasets.

More detailed information about Dac-Man's features and functionality
can be found in the [*Using Dac-Man*](../use/general/) section of the documentation.

!!! important
    This guide assumes you have installed Dac-Man as described in the [installation instructions](../install).

## A step-by-step example running `diff`

### Comparing directories

Dac-Man is able to compare directories of files as well as individual files for changes.

After activating Dac-Man's environment,
navigate to the `examples` directory of Dac-Man's source code repository.
Then, to compare two directories for changes, run the `dacman diff` command with the directories as arguments:

```sh
cd dac-man/examples
dacman diff data/simple/v0 data/simple/v1
```

This comparison will produce output that lists the number of changes between the two folders in five categories.
For more information about Dac-Man's output, refer to the [*Outputs*](../use/general/#outputs) subsection.

```txt
Added: 1, Deleted: 1, Modified: 1, Metadata-only: 0, Unchanged: 1
```

### Comparing specific files

To compare two specific files for changes, run the `dacman diff` command with the `--datachange` option.
The `--script` option allows you to specify a particular change analysis script, in this case the built-in Unix `diff` tool.

```sh
dacman diff data/simple/v0 data/simple/v1 --datachange --script /usr/bin/diff
```

This comparison will produce output that lists the number of changes to data values between these folders.
The output will also list specific changes that the analysis script (in this case `diff`) found.

```diff
Added: 1, Deleted: 1, Modified: 1, Metadata-only: 0, Unchanged: 1
1c1
< foo
\ No newline at end of file
> hello
\ No newline at end of file
```

## Using Dac-Man plug-ins to compare files

Dac-Man plug-ins allow to analyze changes between file contents in a more specialized way,
depending on the file type.

### Enabling built-in plug-ins

Dac-Man comes with built-in plug-ins for CSV and HDF5 files.

To enable a particular plug-in, its required additional dependencies must be installed.
Follow [these steps](../install/dependencies/) to install dependencies for all of Dac-Man's built-in plug-ins.

Once a plug-in has been enabled,
it will automatically be used by Dac-Man when comparing files of the supported type.

### Using the CSV plug-in

As one of Dac-Man's built-in plug-ins, after enabling it by installing its dependencies,
the CSV plug-in will be used automatically when comparing CSV files.

The `examples/data/csv` directory contains the two example files `A.csv` and `B.csv`.

To test the Dac-Man CSV plug-in with these two files,
run this command from the `examples` directory:

```sh
dacman diff data/csv/A.csv data/csv/B.csv
```

### Using the HDF5 plug-in

As one of Dac-Man's built-in plug-ins, after enabling it by installing its dependencies,
the HDF5 plug-in will be used automatically when comparing HDF5 files.

The `examples/data/hdf5` directory contains the two example files `A.h5` and `B.h5`.

To test the Dac-Man HDF5 plug-in with these two files,
run this command from the `examples` directory:

```sh
dacman diff data/hdf5/A.h5 data/hdf5/B.h5
```

### Using plug-ins when comparing entire directories

Plug-ins are also supported when using Dac-Man to compare entire directories with the `--datachange` option.
When Dac-Man detects a modification in a file of a supported type,
it will automatically choose the corresponding plug-in to perform the comparison bet.

The `examples/data/plugin_test` directory contains the two sub-directories `v0` and `v1`,
containing multiple files of the types supported by the built-in plug-ins.

To test the built-in plug-ins, after installing the dependencies,
run this command from the `examples` directory:

```sh
dacman diff data/plugin_test/v0 data/plugin_test/v1 --datachange
```

### Additional information

For more information on Dac-Man's plug-in framework, refer to these sections of the documentation:

- [Using Dac-Man's plug-ins](../plugins/)
