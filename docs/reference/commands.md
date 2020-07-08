# Dac-Man Commands and Output

## Command-line

Dac-Man enables change capture and analysis with four simple steps,
providing users with flexibility when identifying and capturing changes.
Dac-Man provides four command-line options to manage each of these steps separately.

<!-- Set table widths so that CLI flags are not split over multiple lines -->
<!-- adapted from: https://stackoverflow.com/a/58338258 -->
<style>
table th:first-of-type {
    width: 35%;
}
table th:nth-of-type(2) {
    width: 65%;
}
</style>

### `scan`

This command scans and saves the directory structure and other metadata related to a data path.
You can specify an optional staging directory, where the metadata information will be saved.

```sh
dacman scan <path> [-s STAGINGDIR] [-i [IGNORE [IGNORE ...]]] [--nonrecursive] [--symlinks]
```

The options to this command are:

| Option | Meaning |
| --- | --- |
| `-s STAGINGDIR` | Directory where filesystem metadata and indexes are saved |
| `-i [IGNORE [IGNORE ...]]` | List of file types to be ignored |
| `--nonrecursive` | Do not scan the directory contents recursively |
| `--symlinks` | Include symbolic links |

### `index`

This command indexes the files, mapping the files to their contents.

```sh
dacman index <path> [-s STAGINGDIR] [-m python,tigres,mpi]
```

The options to this command are:

| Option | Meaning |
| --- | --- |
| `-s STAGINGDIR` | Directory where filesystem metadata and indexes are saved |
| `-m python,tigres,mpi` | Index manager for parallelizing the index creation. Possible values are `python`, `mpi` and `tigres`. By default, it uses the Python multiprocessing module (`manager=python`) that is suitable for parallelizing on a single node. For multi-node parallelism, users can select between MPI (`manager=mpi`) or tigres (`manager=tigres`) |

### `compare`

This command examines and calculates the different types of changes between two datapaths.

```sh
dacman <oldpath> <newpath> [-s STAGINGDIR]
```

The options to this command are:

| Option | Meaning |
| --- | --- |
| `-s STAGINGDIR` | Directory where filesystem metadata and indexes are saved |

### `diff`

This command retrieves changes between two datapaths.

```sh
dacman diff <oldpath> <newpath> [-s STAGINGDIR] [-o OUTDIR] [--script SCRIPT] [--datachange] [-e default,threaded,mpi,tigres]
```

The options to this command are:

| Option | Meaning |
| --- | --- |
| `-s STAGINGDIR` | Directory where filesystem metadata and indexes are saved |
| `-o OUTDIR` | Directory where the summary of changes is saved |
| `--script SCRIPT` | User-defined script for analyzing data changes |
| `--datachange` | Calculate data-level changes in addition to file-level changes |
| `-e default,threaded,tigres,mpi` | Type of executor (or runtime) for parallel data change capture. The options are: `default`, `threaded`, `tigres`, `mpi`. The `default` option uses single-threaded execution. The `threaded` option uses the Python multiprocessing module that is suitable for parallelizing on one node. For multi-node parallelism, users can select between MPI or tigres. |

---

In addition to these four commands, Dac-Man also provides two additional commands for cleanup and metadata management.

### `clean`

This option removes all the indexes and cache information associated with the specified directories.

```sh
dacman clean <path> [path ...]
```

The arguments to this command are:

| Option | Meaning |
| --- | --- |
| `path` | Path to data directories |

### `metadata`

This command allows users to add user-defined metadata for a data directory.

```sh
dacman metadata [-m METADATA] [-s STAGINGDIR] insert,retrieve,append <datapath>
```

The options to this command are:

| Option | Meaning |
| --- | --- |
| `-s STAGINGDIR` | Directory where filesystem metadata and indexes are saved |
| `-m METADATA` | User-defined metadata information |
| `insert,retrieve,append` | Options related to user-defined metadata information |
| `datapath` | Path to the data directory |

## Outputs

Dac-Man prints the summary of changes on standard output.
The summary lists the number of changes between two datasets.

An example output looks like below:

```txt
Added: 1, Deleted: 1, Modified: 1, Metadata-only: 0, Unchanged: 1
```

You can opt to save a more detailed output by specifying the output directory where the detailed change information will be saved:

```sh
dacman diff /path/to/old/data /path/to/new/data -o output
```

The `output/` directory contains a list of files with detailed information about the changes.
It also contains a summary of the change information as:

```yaml
# output/summary

counts:
  added: 1
  deleted: 1
  metaonly: 0
  modified: 1
  unchanged: 1
versions:
  base:
    dataset_id: /path/to/old/data
    nfiles: 3
  revision:
    dataset_id: /path/to/new/data
    nfiles: 3
```
