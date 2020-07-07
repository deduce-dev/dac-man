# Using Dac-Man's Plug-in Framework

The Dac-Man plug-in framework allows users to implement their own plug-ins
for comparing files and datasets of different types and formats.
Dac-Man also provides built-in plug-ins for a variety of popular scientific data formats,
including hierarchical datasets (e.g [HDF5](../../plugins/hdf5)),
image files (e.g. [FITS](../../plugins/default), [EDF](../../examples/hdf5-edf)),
and tabular data (e.g. [CSV](../../plugins/csv), [Excel](../../examples/excel)).

## Usage

Dac-Man automatically selects which plug-in to use at runtime based on file types,
choosing from the plug-ins installed inside the `dacman/plugins` directory.
Users can specify which plug-in to use in several ways, described below.

### Configuring plug-in selection for specific file types

When Dac-Man is run for the first time, a plug-ins configuration file is created in the user's home directory,
under `$HOME/.dacman/config/plugins.yaml`.

Users can edit this file to override the default behavior and customize the selection of a plug-in for comparisons of specific file types.
This file may contain any of the available plug-ins registered with the Dac-Man plug-in framework.

### Specifying custom analysis scripts via the command line

Dac-Man also allows users to use their own change analysis scripts instead of the available plug-ins,
by specifying the path to an executable with the `--script` option when invoking Dac-Man via the command-line interface:

```sh
dacman diff <file1> <file2> --script /path/to/myscript
```

For example, to use the Unix `diff` tool to compare all the modified files in the directories `dir1` and `dir2`,
run the following command:

```sh
dacman diff /path/to/dir1 /path/to/dir2 --datachange --script /usr/bin/diff
```

The `--datachange` option tells to compare the data within the files of the two directories.

!!! example
    An example showing how to use custom scripts for data change analysis can be found [here](../../examples/script).

### Using the Dac-Man API

In addition to using the `dacman` command-line utility,
users can write their own change analysis pipelines using the Dac-Man API.
The API also provides the necessary module for users to specify a plug-in in their code.

```py
from dacman import Executor, DataDiffer
from dacman.plugins.default import DefaultPlugin

def my_diff(file1, file2):
    comparisons = [(file1, file2)]
    differ = DataDiffer(comparisons, executor=Executor.DEFAULT)
    differ.use_plugin(DefaultPlugin)
    differ.start()
```

Users can also create and register their own plug-ins in Dac-Man.
The [Plug-in API](../../api/plugins) section describes the Dac-Man plug-in API
that can be used to create user-defined plug-ins in Dac-Man.

!!! example
    An example showing how to extend Dac-Man's built-in plug-ins, and use Dac-Man's API to incorporate them into custom analysis scripts can be found [here](../../examples/csv-simple).
