# Using Dac-Man's Plug-in Framework

Scientific datasets come in various formats and data types.
It is not a sustainable solution to compare files and datasets of different types in a single way.
For example, image files are very different from text files,
and therefore need to be compared differently.
Additionally, the structure and format of files varies substantially across scientific disciplines.

The Dac-Man plug-in framework allows users to implement their own plug-ins
for comparing files and datasets of different types and formats.
Additionally, Dac-Man also provides built-in plug-ins for a variety of popular scientific data formats,
including hierarchical datasets (e.g [HDF5](../../plugins/hdf5)),
image files (e.g. [FITS](../../plugins/default), [EDF](../../examples/hdf5-edf)),
and tabular data (e.g. [CSV](../../plugins/csv), [Excel](../../examples/excel)).

## Usage

The plug-ins in Dac-Man are generally placed inside the `dacman/plugins/` directory of the source code.
Dac-Man automatically selects the specific plug-in at runtime based on the file types.
However, users can also specify explicitly which plug-in to use for data comparisons.

Generally, plug-ins in Dac-Man can be specified in three different ways,
described below.

### Plug-ins configuration

When Dac-Man is installed, a plug-ins configuration file is created in the user's home directory,
under `$HOME/.dacman/config/plugins.yaml`.

This file may contain all the registered internal plug-ins in Dac-Man.
Users can edit this file to specify the selection of a plug-in for specific file-type comparisons.

### Command-line

Dac-Man also allows users to use their own change analysis scripts as plug-ins.
To use this, users need to provide the `-p/--plugin` option when invoking Dac-Man:

```sh
dacman diff <file1> <file2> --plugin /path/to/myscript
```

For example, to use the Unix `diff` tool to compare all the modified files in the directories `dir1` and `dir2`,
run the following command:

```sh
dacman diff /path/to/dir1 /path/to/dir2 --detailed --plugin /usr/bin/diff
```

The `--detailed` option tells to compare the data within the files of the two directories.

### Dac-Man API

Users can write their own change analysis pipelines using the Dac-Man API.
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
