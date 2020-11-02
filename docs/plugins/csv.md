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

## Usage

### Requirements

The `pandas` package is required as an additional dependency for this plug-in.

!!! tip
    These [instructions](../../install/dependencies) describe how to install dependencies for all of Dac-Man's included plug-ins in a single step.

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

## API

The parameters described in this section are the core options of this plug-in,
used to specify additional information about the source data
to obtain more accurate and specific results from the change analysis.

If no option is given, Dac-Man will perform the analysis using the default values,
using table data in the `orig` format as described above.
After running the analysis for the first time,
users can then gradually add the necessary information,
proceeding iteratively after checking the results obtained for each set of parameters.

!!! example
    An example showcasing the use of these options to adapt the CSV plug-in to custom data is available [here](../../../examples/csv-simple).

### `comment_char`

Lines in the source file starting with this character (string of length 1) are considered comments, and are not loaded in the table.
The default value for this option is `#`, matching the conventional way of incorporating comments into CSV files.

### `header_pos`

Indicate the position (integer, 0-based) of the table row containing the header,
which will be used to set the column names.

### `skip_lines`

Indicate the positions (list of integers, 0-based) of lines to be excluded from the table.

### `index`

Choose how to set the table index.
The table index is a special column whose values are the row labels,
analogous to the primary key in a relational database table.

The possible values for `index` are:

| value | meaning |
|:-|:-|
| `grididx` | (default) Table rows are labeled based on the order in which they appear in the source file, excluding commented lines, starting from 0 |
| `lineno` | Table rows are labeled based on the corresponding line number in the source file (1-based). Commented lines are counted (but not included in the table) |
| any valid column name | Table rows are labeled based on the values in the column. The values should be unique (even though this is not explicitly enforced) |

!!! remark
    Values in the two source tables are aligned for comparison using the index, and so different ways of setting the index can have a significant effect on the change analysis result. Refer to [this section](../../../examples/csv-simple/#setting-the-index) of the example for more information.

### `process_func`

A function used to apply custom data processing on the data table.

The function must take a `pandas.DataFrame` object in input and return a `pandas.DataFrame`, e.g.:

```py
def my_custom_processing(df):
    """
    Exclude rows with low temperatures
    since they're not relevant for this analysis
    """

    filtered_df = df[df['temperature'] > 20.]

    return filtered_df
```

### `column_renames`

Set new column names to specify columns having different names in the two source files.

Column names are used to determine which column from each of the two sources will be associated for comparison.
If a data column is present in both sources and refers to the same data, but with different names (e.g. `surface_area` in `A.csv` and `area_km2` in `B.csv`),
it will be treated as two separate columns being added to `B.csv` (`area_km2`) and deleted from `A.csv` (`surface_area`).

By providing a mapping between the two names, e.g. `column_renames = {'surface_area': 'area_km2'}`, the column(s) will be renamed before the comparison,
and the new name used in the rest of the analysis.

!!! tip
    The original name is recorded by Dac-Man as part of the column metadata, and will appear in the change analysis as a modified value.

### `dtype`

Choose how to set column data dtypes (`dtypes`).

Possible values are:

| value | meaning |
|:-|:-|
| `None` | (default) No conversion is attempted, and existing dtypes are kept. If no other conversion is applied to the table (e.g. in `process_func()`), all table values will be compared as text |
| `True` | Automatic conversion to more specific dtypes will be attempted on columns with text dtype. By default uses `pandas` built-in functions `to_datetime()` and `to_numeric()` |
| Mapping `{colname: dtype}` | Used to set specific per-column dtypes, using any argument valid for `pandas.DataFrame.astype()` |
