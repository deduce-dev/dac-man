# Additional environments and use cases

## Comparing datasets with read-only access

If the data directories have read-only access,
the metadata and indexes can be stored in a user-defined location `my_staging_dir` using the `-s` option:

```sh
dacman index datadir -s my_staging_dir
```

## Comparing datasets at two different sites

To compare datasets at two different sites,
one strategy is to create indexes in a user-defined location (as shown in the previous step),
and copy the staged indexes to a common location, e.g. `my_shared_index_location`.
The changes can then be retrieved using:

```sh
dacman diff local_dir remote_dir -s my_shared_index_location
```
