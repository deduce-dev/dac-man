# The Dac-Man Excel Plug-in

The Dac-Man Excel plug-in is capable of detecting and analyzing changes between two Excel spreadsheets,
interpreted as tabular data.
Users can optionally specify a subset of the whole spreadsheet as the tabular data to be analyzed,
allowing more specific comparisons.

The Excel plug-in is closely related with the Dac-Man CSV plug-in.
For more information, refer to the CSV plug-in [documentation](../csv/).

## Usage

### Requirements

The `pandas` and `xlrd` packages are required as additional dependencies for this plug-in.

!!! tip
    These [instructions](../../install/dependencies) describe how to install dependencies for all of Dac-Man's built-in plug-ins in a single step.

### Using the Excel Plug-in

As part of the built-in Dac-Man plug-ins, once its dependencies have been installed,
the Excel plug-in will be used by default when comparing Excel files.

The [`examples/plugin_test/`](https://github.com/dghoshal-lbl/dac-man/blob/master/examples/plugin_test/) directory of the Dac-Man source code repository
contains two example Excel files in the two sub-directories `v0` and `v1`.
To compare these example files, navigate to the `examples/plugin_test` directory
and run `dacman diff` with the `--datachange` option:

```sh
cd examples/plugin_test
dacman diff v0 v1 --datachange
```
