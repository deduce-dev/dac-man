# Configuration and Customization

## Staging

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
This is specifically useful when the datasets to be compared are located on different systems.
The example below shows how can the staged indexes and metadata information be copied and compared for finding changes,
without copying the data itself.

```sh
scp -r user:pass@~/.dacman/data/ /path/to/mystage/
dacman diff /path/to/localdir/ /remotedir/ -s /path/to/mystage
```

## Plug-ins

By default, Dac-Man compares the data by transforming file data into Dac-Man records,
that use one-dimensional arrays as their underlying data structure.

You can also use plug-ins by providing external scripts.
You can use your own custom scripts as plug-ins by simply providing the path to the script.
For example, `myscript` can be used as a plug-in:

```sh
dacman diff /old/path/file1 /new/path/file1 --script myscript
```

The command above uses `myscript` as an external plug-in to compare the contents of files `/old/path/file1` and `/new/path/file1` instead of the default data comparator.
If you want to use Unix diff to compare all the modified files in the directories `dir1` and `dir2`,
run the following command:

```sh
dacman diff /path/to/dir1 /path/to/dir2 --datachange --script /usr/bin/diff
```

The `--datachange` option tells to compare the data within the files of the two directories.

Finally, you can build your own plug-ins by extending the `ComparatorBase` class.
Please refer to the [plug-ins usage section](../plugins) for details.

## Logging

Dac-Man uses the standard Python logging for creating execution logs.
The default logging configuration is saved in the `$HOME/.dacman/config/logging.yaml` file.
Dac-Man logs all INFO level messages, and prints messages with levels equal to or over the WARNING level.
However, you can configure the logging as per your requirement by modifying the configuration file.
