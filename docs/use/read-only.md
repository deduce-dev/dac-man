# Comparing datasets with read-only access

If the data directories have read-only access,
the metadata and indexes can be stored in a user-defined location `my_staging_dir` using the `-s` option:

```sh
dacman index datadir -s my_staging_dir
```
