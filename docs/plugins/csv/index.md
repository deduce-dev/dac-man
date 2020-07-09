# The Dac-Man CSV plug-in

## Introduction

The Dac-Man CSV plug-in allows users to detect, analyze, and display changes in CSV (Comma-Separated Values) files.

By including the tabular data content of the source files in the change analysis,
Dac-Man provides several advantages over a line-by-line analysis
performed using generic tools for text files such as `diff`, including:

- Considering features specific to the CSV format,
  including widely-used conventions such as comment characters and embedded metadata
- Providing change information for individual values in each row (line),
  rather than only for the whole line
- More specific change analysis of the tabular data content
  by interpreting table values as numeric data rather than text
- Obtaining domain-specific information in the change analysis by allowing users
  to easily customize and extend all parts of the change analysis pipeline

## Usage

### Dependencies

The `pandas` package is required as an additional dependency for this plug-in.

!!! tip
    These [instructions](../../install/dependencies) describe how to install dependencies for all of Dac-Man's built-in plug-ins in a single step.

### Using the CSV Plug-in

The included CSV plug-in will be used by Dac-Man to compare CSV files when its dependencies are installed.

The [`examples/plugin_test/`](https://github.com/deduce-dev/dac-man/blob/master/examples/plugin_test/) directory of the Dac-Man source code repository
contains two example CSV files in the two sub-directories `v0` and `v1`.
To compare these example files, navigate to the `examples/plugin_test` directory
and run `dacman diff` with the `--datachange` option:

```sh
cd examples/plugin_test
dacman diff v0 v1 --datachange
```

## Key concepts

### CSV files as text and data tables

CSV files are text files that store tabular data.
This means that, when analyzing CSV files for changes,
we can interpret them in two different ways:

- As text, comparing the contents and metadata of the source files
- As data tables, comparing the two tables created from the source files content

The text interpretation requires only minimal assumptions about the structure of the source files,
but the additional information available over standard line-based tools for comparing text files is limited.

Conversely, since converting a CSV file to a table is not an unambiguously-defined operation,
the data table interpretation requires several assumptions about the source data,
but can lead to richer and more meaningful results of the change analysis.

By default, the plug-in includes both interpretations in the change analysis,
and offers the possibility of gradually adding assumptions about the sources
leading to correspondingly more specific results.

### Original and calculated table formats

CSV files do not have the capability of retaining information about the data type (int, float, datetime, etc.) of the data stored in them.
Thus, strictly speaking, when creating a table from a CSV files all values should be treated as text.

At the same time, having more specific data types when analyzing changes makes it possible to have more relevant comparisons.
For example, consider the two values `a = 2019-01-11` and `b = 1/11/2019`,
representing the same date written in two different formats.
By comparing them as text, the result would be that they are different, since `a != b`.
If we convert them to a `datetime` data type before comparing them,
the difference in formats will be properly accounted for during the conversion,
resulting in `a = datetime(2019, 1, 11)` and `b = datetime(2019, 1, 11)`, i.e. `a == b`.

Also, using more specific data types allows to compute the delta `a - b` between two values in a meaningful way,
which is not possible when considering the values as text.
For example, if `a = datetime(2019, 1, 11)` and `b = datetime(2019, 1, 13)`, `a - b = timedelta(-2 days)`.

To properly account for both of these aspects, the Dac-Man CSV plug-in creates two tables in two different formats to manage the tabular data.

First, the content of the source file is loaded in a table applying the least possible amount of processing.
The format of this table is called `orig`, for "original".
In particular:

- All valid (uncommented) lines are loaded
- All table values are treated as text
- Table columns are identified with an integer (`colidx`) instead of using names from the header in the file
- Table rows are identified using the line number (`lineno`) of the source file.
  This is 1-based, i.e. the first line in the file has `lineno = 1`
  
Then, several processing steps are applied to the `orig` table according to the options set in the plug-in.
The resulting table is in the `calc` format (for "calculations"),
since it will be used for the change metrics calculations of table values.

Depending on the actual values of the options, the differences with the `orig` format are:

- Column names from a header in the original table are used to identify table columns
- Table rows are identified with values from a specific column
- Column values are converted from text to more specific data types
