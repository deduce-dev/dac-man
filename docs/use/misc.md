# Additional settings and use cases

## Setting the location of the staging area

When indexing a dataset, Dac-Man uses a staging area to save all metadata and index information.
Each directory in the staging area uniquely identifies each dataaset (using a hash representation of the dataset path) indexed by Dac-Man.
Users can customize this location when analyzing read-only datasets or comparing files on different systems.

The default staging area is located in `$HOME/.dacman/data`.
Users can change the staging area path through the command-line with this command:

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
