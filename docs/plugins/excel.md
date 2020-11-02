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
    These [instructions](../../install/dependencies) describe how to install dependencies for all of Dac-Man's included plug-ins in a single step.

### Using the Excel Plug-in

The included Excel plug-in will be used by Dac-Man to compare Excel files when its dependencies are installed.

The [`examples/plugin_test/`](https://github.com/deduce-dev/dac-man/blob/master/examples/plugin_test/) directory of the Dac-Man source code repository
contains two example Excel files in the two sub-directories `v0` and `v1`.
To compare these example files, navigate to the `examples/plugin_test` directory
and run `dacman diff` with the `--datachange` option:

```sh
cd examples/plugin_test
dacman diff v0 v1 --datachange
```

## API

By default, the Excel plug-in will compare the source files by loading the content of the first worksheet as a single table.

It is also possible to provide options to provide a more specific and target change analysis.
These options are described in the following section.

### `worksheet_id`

Define which worksheet should be considered in both source files for the change analysis.
Both positional indices (e.g. `0` for the first worksheet in the workbook) and names can be used.

Default: `0`.

### `table_range`

Define the subset of the worksheet from which the tabular data will be loaded.
This can be useful if a spreadsheet contains multiple tables and/or additional content,
and the goal of the change analysis is to isolate and compare only a single table across the two input sources.

By default, the entire worksheet is loaded.

#### Example

for example, to load the subrange between rows 5 and 15, and columns C to H (both inclusive):

```py
opts = {
    'table_range': {
        'row_start': 5,
        'row_end': 15,
        'col_start': 'C',
        'col_end': 'H'
    }
}
```

### `header`

Define which row(s) is used as the header of the table.

This is often used to store the names of the table columns,
but often additional rows are used for other metadata (e.g. measurement units, reference values, etc).

If given, the `header` specification will be used to locate the rows containing metadata,
which will be extracted from the table,
removed from the table values, and stored as metadata for the corresponding columns.
This is turn will allow to e.g. preserve the data type of the table values,
allowing more specific comparisons during the change analysis.

#### Syntax

If the value of `header` is given, it should be a mapping (Python `dict`) with the following structure:

| Key | Possible values | Description |
| - | - | - |
| `pos` | `abs`, `rel` | Determines if the integers given to the other keys should be consider as the row number in the spreadsheet (`abs` for absolute position), or relatively to the start of the range, starting from 0 (`rel`) |
| Any string *S* | Any integer *N* | Indicate that the column metadata property *S* should be extracted from the row *N*, according to the specification given with `pos`. Any number of *(S, N)* pairs can be given to extract multiple properties |
| `name` | Any integer *N* | If the key `name` is given, it will be used as the column name instead of the spreadsheet column name. |

#### Example

For example, consider the following portion of a spreadsheet, starting at row 21:

| | A | B | C | D |
|: - | - | - | - | - |
|21| Element | Atomic number | Density | Melting point |
|22| | | g/cm^3 | deg_C |
|23| Au | 79 | 19.30 | 1068.4 |
|24| Ag | 47 | 10.49 | 961.78 |
|25| Pt | 78 | 21.45 | 1768.3 |
|26| Cu | 29 | 8.96 | 1084.62 |

We can see that the first row of the table (spreadsheet row 21) contains the column names,
and the second row (spreadsheet row 22) contains the measurement units used for the column values.

We can express this structure using the `header` option,
assigning the `name` property to the column name, and `units` for the units.

Using `'pos': 'abs'`:

```py
opts = {
    'header': {
        'pos': 'abs',
        'name': 21,
        'units': 22,
    }
}
```

Or, equivalently, using `'pos': 'rel'`:

```py
opts = {
    'header': {
        'pos': 'rel',
        'name': 0,
        'units': 1,
    }
}
```

With these options, the column metadata will be extracted from the table, and stored (and later compared during the change analysis) separately from the table values.

*Table*

| Element | Atomic number | Density | Melting point |
| - | - | - | - |
| Au | 79 | 19.30 | 1068.4 |
| Ag | 47 | 10.49 | 961.78 |
| Pt | 78 | 21.45 | 1768.3 |
| Cu | 29 | 8.96 | 1084.62 |

*Column metadata*

```py
[
    {
        'colidx': 'A',
        'name': 'Element',
        'units': '',
    },
    {
        'colidx': 'B',
        'name': 'Atomic number',
        'units': '',
    },
    {
        'colidx': 'C',
        'name': 'Density',
        'units': 'g/cm^3',
    },
    {
        'colidx': 'D',
        'name': 'Melting point',
        'units': 'deg_C',
    }
]
```

### `index`

Choose how to set the table index.
The table index is a special column whose values are the row labels,
analogous to the primary key in a relational database table.

The possible values for `index` are:

| Value | Meaning |
|:-|:-|
| `None` | (default) Table rows are labeled based on the order in which they appear in the source file, starting from 0 |
| `orig` | Table rows are labeled based on the original spreadsheet row number in the source file. Skipped rows are counted, but not included in the table |
| Any column name | Table rows are labeled based on the values in the column. The values should be unique (even though this is not explicitly enforced) |

### Other options

For information on the `column_renames` and `dtype` options, refer to the corresponding sections in the CSV plug-in API [documentation](../csv/#column_renames).
