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

### Using Dac-Man plug-ins to compare files

Dac-Man built-in plug-ins allow to analyze changes in a more specialized way, depending on the file type.
When files of a supported type are compared,
Dac-Man will automatically choose the corresponding plug-in to perform the comparison.

To enable a particular plug-in, its required additional dependencies must be installed.
Follow [these steps](../install/dependencies/) to install dependencies for all of Dac-Man's built-in plug-ins.

After installing the dependencies, run the following command to test Dac-Man file comparison
with example directories containing files of the types supported by the built-in plug-ins:

```sh
dacman diff data/plugin_test/v0 data/plugin_test/v1 --datachange
```

For more information on Dac-Man's plug-in framework, refer to these sections of the documentation:

- [Using Dac-Man's plug-ins](../use/plugins/)
