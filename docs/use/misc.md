# Additional environments and use cases

## Setting the location of the staging area

For every dataset, Dac-Man saves all metadata and index information in a staging area.
Each directory in the staging area uniquely identifies the dataset (using a hash representation of the dataset path) indexed by Dac-Man.
By default, this staging area for is located in `$HOME/.dacman/data`.
However, the staging area can be changed to a custom location through
the command-line.
You can change the staging area by using the following command:

```sh
dacman index mydir/ -s mystage
```

The command above creates the indexes inside `mystage` directory.
You can copy or move these indexes to compare and calculate the changes,
without necessarily copying or moving the data.
This is useful for cases when access to the datasets is limited or restricted, as illustrated in the following examples.

### Comparing datasets with read-only access

If the data directories have read-only access,
the metadata and indexes can be stored in a user-defined location `my_staging_dir` using the `-s` option:

```sh
dacman index datadir -s my_staging_dir
```

### Comparing datasets at two different sites

To compare datasets at two different sites,
one strategy is to create indexes in a user-defined location (as shown in the previous step),
and copy the staged indexes to a common location, e.g. `my_shared_index_location`.
The changes can then be retrieved using:

```sh
dacman diff local_dir remote_dir -s my_shared_index_location
```
