# CSV Plug-in API

## `CSVPlugin` main options

The parameters described in this section are the core options of this plug-in,
used to specify additional information about the source data
to obtain more accurate and specific results from the change analysis.

In line with Dac-Man's design principles, the user is given full choice
about the amount of additional information to provide
(and, correspondingly, the level of detail and specificity of the change analysis).

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
