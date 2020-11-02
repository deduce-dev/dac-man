# Dac-Man Quick Start Guide

This guide serves as a starting point for using Dac-Man.
In this guide, we will demonstrate how to use the Dac-Man data change tool to compare two
versions of a sample dataset.

!!! important
    This guide assumes you have installed Dac-Man as described in the [installation instructions](../install).
    Alternatively, you can use Binder to try Dac-Man without needing to install it locally.
    See [*Running Dac-Man in Binder*](#running-dac-man-in-binder) for instructions.

## A step-by-step example running `diff`

### Comparing directories

Dac-Man is able to compare directories of files as well as individual files for changes.

First, activate Dac-Man's environment, then navigate to the `examples`
directory of Dac-Man's source code repository. Next, compare two directories
for changes by running the `dacman diff` command with the directory paths as
arguments:

```sh
cd dac-man/examples
dacman diff data/simple/v0 data/simple/v1
```

This comparison will produce output that lists the number of changes between the two folders in five categories.
For more information about Dac-Man's output, refer to the [*Outputs*](../reference/commands/#outputs) subsection.

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

### Enabling included plug-ins

Dac-Man comes with included plug-ins for CSV, HDF5, and JSON files.

To enable a particular plug-in, its required additional dependencies must be installed.
Follow [these steps](../install/dependencies/) to install dependencies for all of Dac-Man's included plug-ins.

Once a plug-in has been enabled,
it will automatically be used by Dac-Man when comparing files of the supported type.

### Using the CSV plug-in

When dependencies are installed, Dac-Man's CSV plug-in will be used automatically when comparing CSV files.

The `examples/data/csv` directory contains the two example files `A.csv` and `B.csv`.

To test the Dac-Man CSV plug-in with these two files,
run this command from the `examples` directory:

```sh
dacman diff data/csv/A.csv data/csv/B.csv
```

### Using the HDF5 plug-in

When dependencies are installed, Dac-Man's HDF5 plug-in will be used automatically when comparing HDF5 files.

The `examples/data/hdf5` directory contains the two example files `A.h5` and `B.h5`.

To test the Dac-Man HDF5 plug-in with these two files,
run this command from the `examples` directory:

```sh
dacman diff data/hdf5/A.h5 data/hdf5/B.h5
```

### Using plug-ins when comparing entire directories

Plug-ins are also supported when using Dac-Man to compare entire directories with the `--datachange` option.
When Dac-Man detects a modification in a file of a supported type,
it will automatically choose the corresponding plug-in to perform the comparison.

The `examples/data/plugin_test` directory contains the two sub-directories `v0` and `v1`,
containing multiple files of the types supported by the included plug-ins.

To test the included plug-ins, after installing the dependencies,
run this command from the `examples` directory:

```sh
dacman diff data/plugin_test/v0 data/plugin_test/v1 --datachange
```

### Additional information

More detailed information about Dac-Man's features and functionality,
can be found in the [*Reference*](../reference/commands/) section of the documentation.

For more information on Dac-Man's plug-in framework, refer to these sections of the documentation:

- [Running Custom Change Analyses](../use/plugins)
- [Dac-Man's plug-in API reference](../reference/plugins-api)

## Running Dac-Man in Binder

With [Binder](https://mybinder.readthedocs.io) you can try Dac-Man in a temporary cloud environment without needing to install on your local machine.

Clicking on this button will create a Dac-Man environment on Binder and open a web terminal: [![badge](https://img.shields.io/badge/launch-binder-579ACA.svg?logo=data:image/png;base64,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)](https://mybinder.org/v2/gh/deduce-dev/dac-man/master?urlpath=/terminals/1)

!!! note
    It might take a few minutes for Binder to setup the environment.

!!! note
    Sample data to try Dac-Man features out will be available in the `examples` directory once the Binder environment is running.

!!! warning
    After a period of inactivity, Binder environment (along with all data that was added by users during the session) are automatically and irreversibly deactivated and destroyed.

### Binder Limitations

Although a valuable tool for distributing test environments, Binder's mode of operation might make it unsuitable for certain workflows and/or datasets.
Make sure to read the [documentation](https://mybinder.readthedocs.io/en/latest/) carefully, in particular the [usage guidelines](https://mybinder.readthedocs.io/en/latest/user-guidelines.html) and the [user privacy policy](https://mybinder.readthedocs.io/en/latest/faq.html#how-does-mybinder-org-ensure-user-privacy).

Outside of a quick evaluation, the recommended way of using Dac-Man is to install it in the users' computing environment.