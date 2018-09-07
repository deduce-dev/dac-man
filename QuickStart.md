# Dac-Man Quick Start Guide
This document will get you started using the Dac-Man data change tool on your personal computer. This guide will help you use the Dac-Man tool to compare two versions of a sample dataset. Having completed this guide you will be ready to use Dac-Man to compare your own datasets.

**This guide assumes you have installed Dac-Man using the installation
instructions in the [README](https://github.com/dghoshal-lbl/dac-man/blob/master/README).**

More detailed information about Dac-Man's features and functionality can be found in other documents.

## A step-by-step example running diff
1. From a terminal navigate to the directory with the Dac-Man source has been downloaded.

2. Next we will try out Dac-Man using a sample dataset by changing directory to `examples/`.

        $ cd examples

    **Dac-Man is able to compare directories of files as well as individual files for changes.**

3. To compare two directories for changes, run the `dacman diff` command with the directories as arguments:

        $ dacman diff data/simple/v0 data/simple/v1

  This comparison will produce output that lists the number of changes between the two folders in five categories. The categories are explained further in the README.

        Added: 1, Deleted: 1, Modified: 1, Metadata-only: 0, Unchanged: 1

3. To compare two specific files for changes, run the `dacman diff` command with the `--datachange` option. The `-a` option allows you to specify a particular change analysis script, in this case the built-in Unix `diff` tool.

        $ dacman diff data/simple/v0 data/simple/v1 --datachange -a /usr/bin/diff

  This comparison will produce output that lists the number of changes to data values between these folders. The output will also list specific changes that the analysis script (in this case `diff`) found.

        Added: 1, Deleted: 1, Modified: 1, Metadata-only: 0, Unchanged: 1
        1c1
        < foo
        \ No newline at end of file
        ---
        > hello
        \ No newline at end of file
