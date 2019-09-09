# Dac-Man Quick Start Guide

This document will get you started using the Dac-Man data change tool on your personal computer.
This guide will help you use the Dac-Man tool to compare two versions of a sample dataset.
Having completed this guide you will be ready to use Dac-Man to compare your own datasets.

More detailed information about Dac-Man's features and functionality
can be found in the [*Using Dac-Man*](../use/desktop) section of the documentation.

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
For more information about Dac-Man's output, refer to the [*Outputs*](../use/desktop/#outputs) subsection.

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

For more information, refer to these sections of the documentation:

- [Installing dependencies for Dac-Man's built-in plug-ins](../install/dependencies/)
- [Using Dac-Man's plug-ins](../use/plugins/)

## Using Binder

Thanks to [Binder](https://mybinder.readthedocs.io), it's possible to try Dac-Man in a temporary cloud environment,
without having to install it.

Clicking on this button will create a Dac-Man environment on Binder and open a web terminal: [![badge](https://img.shields.io/badge/launch-binder-579ACA.svg?logo=data:image/png;base64,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)](https://mybinder.org/v2/gh/dghoshal-lbl/dac-man/master?urlpath=/terminals/1)

!!! note
    It might take a few minutes for Binder to setup the environment.

!!! warning
    After a period of inactivity, Binder environment (along with all data that was added by users during the session) are automatically and irreversibly deactivated and destroyed .

### Limitations

Although a valuable tool for distributing test environments, Binder's mode of operation might make it unsuitable for certain workflows and/or datasets.
Make sure to read the [documentation](https://mybinder.readthedocs.io/en/latest/) carefully, in particular the [usage guidelines](https://mybinder.readthedocs.io/en/latest/user-guidelines.html) and the [user privacy policy](https://mybinder.readthedocs.io/en/latest/faq.html#how-does-mybinder-org-ensure-user-privacy).

Outside of a quick evaluation, the recommended way of using Dac-Man is to [install](../install) it in the users' computing environment, and run it on a [personal computer](../use/desktop) or on an [HPC cluster](../use/hpc).
