
# The Dac-Man CSV plug-in

## Introduction

The Dac-Man CSV plug-in allows to detect, analyze, and display changes in CSV (Comma-Separated Values) files.

By including the tabular data content of the source files in the change analysis,
Dac-Man provides several advantages over a line-by-line analysis
performed using generic tools for text files such as `diff`, including:

- Considering features specific to the CSV format,
  including widely-used conventions such as comment characters and embedded metadata
- Providing change information for individual values in each row (line),
  rather than only for the whole line
- Collecting change metrics specific to the tabular data content,
  by comparing values as e.g. numeric values rather than text
- Obtaining domain-specific information in the change analysis by allowing users
  to easily customize and extend all parts of the change analysis pipeline

## Installation

The pandas package is required as an additional dependency for this plug-in.

pandas can be installed with `conda`, or alternatively using `pip`.
From the environment where Dac-Man is installed, run:

if using `conda`:

```sh
conda install pandas
```

if using `pip`:

```sh
pip install pandas
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

To properly account for both of these aspects, the Dac-Man CSV plug-in creates two tables in two different formats.uses a dual format when creating the data table.

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

The [Examples](#examples) section contains a change analysis workflow showcasing in detail the use of these options.

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
    Values in the two source tables are aligned for comparison using the index, and so different ways of setting the index can have a significant effect on the change analysis result. Refer to the Examples section for more information.

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
| Mapping `{colname: dtype}` | Used to set specific per-column dtypes, using any argument valid for `pandas.DataFrame.astype()`.

## Examples

### Main options

This example illustrates how the different options can be added gradually to improve the accuracy of the change analysis.

In this example, we perform an analysis of the changes between the files `A.csv` and `B.csv`:


```csv
# a single commented line
site_id,message,date,temperature
C,Some text,8/15/2019,24.1
A,Some other text,3/2/2019,35.3
B,,1/1/2018,42.8
```


```csv
# a 
# longer
# comment
# spanning
# several
# lines
site_id,temperature,message,day
B,42.1,Some new text,01/01/2018
# some random comments in the middle
A,35.3,Some other text,03/02/2019
C,24.1,Some text,09/15/2019
```



Since they contain only a few lines, we are able to notice some of the differences by looking at the two files.
Even though the tabular data itself is very similar, there are several differences in the format and the structure on the two files:

- `B` contains additional comments
- Corresponding rows are not in the same order
- The order of values in the same row is different
- The values appearing under the field `date` in `A` appear under `day` in `B`
- The values for `date`/`day` use different conventions to represents date values (with/without leading zeros)

By running `dacman diff A.csv B.csv` with the default options, we obtain these change statistics:


```txt
percent change: 87.50%
      frac_changed  n_added  n_changed  n_deleted  n_modified  n_unchanged  \
name                                                                         
0              0.5        0          2          0           2            2   
1              1.0        1          4          0           3            0   
2              1.0        0          4          0           4            0   
3              1.0        0          4          0           4            0   

        status  
name            
0     MODIFIED  
1     MODIFIED  
2     MODIFIED  
3     MODIFIED  
```



The complete output contains more information about each part of the analysis.

The `file` section contains the change metrics using information about the source files.
It is calculated in the `CSVPlugin.compare_file()` method.

Dac-Man detected changes in the `filename`, `n_lines`, `n_lines_commented`, and `n_chars` metadata properties,
while the `path_parent` and `n_lines_uncommented` are the same in both files.


```json
{
    "file": {
        "status": "MODIFIED",
        "metadata": {
            "common": {
                "path_parent": "/tmp",
                "n_lines_uncommented": 4
            },
            "changes": {
                "filename": {
                    "a": "A.csv",
                    "b": "B.csv"
                },
                "n_lines": {
                    "a": 5,
                    "b": 11
                },
                "n_lines_commented": {
                    "a": 1,
                    "b": 7
                },
                "n_chars": {
                    "a": 134,
                    "b": 215
                }
            }
        }
    }
}
```



The change percentage is high compared to our preliminary inspection of the sources,
so it is possible that some of the changed detected with the most general options are false positives.
We will repeat the analysis, tweaking the plug-in options based on our knowledge about the structure of the source data.

#### Creating a specialized plug-in

!!! tip
    For detailed instructions on creating and registering custom plug-in classes in Dac-Man, refer to the [Using Plugins](../../use/plugins) section.

We start from creating the plug-in implementing our customizations by extending the `CSVPlugin` class:

```py
# in dacman/plugins/my_csv_plugin.py

from dacman.plugins.csv import CSVPlugin

class MyCustomCSVPlugin(CSVPlugin):
    pass
```

#### Setting column names from the header

We start from selecting the position of the row containing the header, from which the column names will be obtained.

This is done by setting the value of `header_pos` in the `calc_options` plug-in attribute, which will be zero since the header is the first row (starting from 0) in both sources:

```py
class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
    }
```

After running `dacman`, the change percentage is slightly lower, accounting for the fact that
the positions of the `temperature` and `message` columns are switched in the sources:


```txt
percent change: 80.00%
             frac_changed  n_added  n_changed  n_deleted  n_modified  \
name                                                                   
site_id          0.666667        0          2          0           2   
message          0.666667        1          2          0           1   
date             1.000000        0          3          3           0   
temperature      0.666667        0          2          0           2   
day              1.000000        3          3          0           0   

             n_unchanged    status  
name                                
site_id                1  MODIFIED  
message                1  MODIFIED  
date                   0  MODIFIED  
temperature            1  MODIFIED  
day                    0  MODIFIED  
```



We can verify this by checking the section dedicated column metadata under the `colidx` property in the complete change analysis output:


```json
{
    "site_id": {
        "status": "MODIFIED",
        "metadata": {
            "common": {
                "name": "site_id",
                "name_header": "site_id",
                "colidx": 0,
                "dtype": "object"
            },
            "changes": {}
        },
        "values": {
            "n_unchanged": 1,
            "n_added": 0,
            "n_deleted": 0,
            "n_modified": 2,
            "n_changed": 2,
            "frac_changed": 0.6666666666666666
        }
    },
    "message": {
        "status": "MODIFIED",
        "metadata": {
            "common": {
                "name": "message",
                "name_header": "message",
                "dtype": "object"
            },
            "changes": {
                "colidx": {
                    "a": 1,
                    "b": 2
                }
            }
        },
        "values": {
            "n_unchanged": 1,
            "n_added": 1,
            "n_deleted": 0,
            "n_modified": 1,
            "n_changed": 2,
            "frac_changed": 0.6666666666666666
        }
    },
    "date": {
        "status": "MODIFIED",
        "metadata": {
            "common": {},
            "changes": {}
        },
        "values": {
            "n_unchanged": 0,
            "n_added": 0,
            "n_deleted": 3,
            "n_modified": 0,
            "n_changed": 3,
            "frac_changed": 1.0
        }
    },
    "temperature": {
        "status": "MODIFIED",
        "metadata": {
            "common": {
                "name": "temperature",
                "name_header": "temperature",
                "dtype": "object"
            },
            "changes": {
                "colidx": {
                    "a": 3,
                    "b": 1
                }
            }
        },
        "values": {
            "n_unchanged": 1,
            "n_added": 0,
            "n_deleted": 0,
            "n_modified": 2,
            "n_changed": 2,
            "frac_changed": 0.6666666666666666
        }
    },
    "day": {
        "status": "MODIFIED",
        "metadata": {
            "common": {},
            "changes": {}
        },
        "values": {
            "n_unchanged": 0,
            "n_added": 3,
            "n_deleted": 0,
            "n_modified": 0,
            "n_changed": 3,
            "frac_changed": 1.0
        }
    }
}
```



#### Setting the index

Table values are compared row-by-row, according to the row labels, or, in equivalent terms,
to which column is set as the table index.
The default option uses the original row index, which results in an erroneous correspondence between rows
because of the rows being ordered differently in the sources.

The values under `site_id` are a good choice for an index, since they are unique within each table, and are the same in both sources.

To set the index, we set the value of `index` is `calc_options`:

```py
class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
        'index': 'site_id',
    }
```

After running `dacman`, the results are:


```txt
percent change: 66.67%
             frac_changed  n_added  n_changed  n_deleted  n_modified  \
name                                                                   
message          0.333333        1          1          0           0   
date             1.000000        0          3          3           0   
temperature      0.333333        0          1          0           1   
day              1.000000        3          3          0           0   

             n_unchanged    status  
name                                
message                2  MODIFIED  
date                   0  MODIFIED  
temperature            2  MODIFIED  
day                    0  MODIFIED  
```



The change percentage is lower, accounting for the fact that the rows are associated correctly, independently on the order in which they appear in the CSV files.

We can verify this by comparing the complete output before and after setting `index = site_id` for e.g. the `values` of the `message` column:


```json
{
    "n_unchanged": 1,
    "n_added": 1,
    "n_deleted": 0,
    "n_modified": 1,
    "n_changed": 2,
    "frac_changed": 0.6666666666666666
}
```


```json
{
    "n_unchanged": 2,
    "n_added": 1,
    "n_deleted": 0,
    "n_modified": 0,
    "n_changed": 1,
    "frac_changed": 0.3333333333333333
}
```



For the sake of comparison, if we instead used `index = lineno`,
the line number where the table row data appears in the source file would be used instead.
Comments are also counted in `lineno`, causing the rows to be completely misaligned:


```txt
percent change: 96.67%
             frac_changed  n_added  n_changed  n_deleted  n_modified  \
name                                                                   
site_id          1.000000        3          6          3           0   
message          0.833333        3          5          2           0   
date             1.000000        0          3          3           0   
temperature      1.000000        3          6          3           0   
day              1.000000        3          3          0           0   

             n_unchanged    status  
name                                
site_id                0  MODIFIED  
message                1  MODIFIED  
date                   0  MODIFIED  
temperature            0  MODIFIED  
day                    0  MODIFIED  
```



For reference, this is how the `calc` tables generated from `A.csv` and `B.csv` look like in the three cases:


```json
{
    "header_pos": 0
}
```


|   __rowidx | site_id   | message         | date      |   temperature |   __lineno |   __rowidx |
|-----------:|:----------|:----------------|:----------|--------------:|-----------:|-----------:|
|          1 | C         | Some text       | 8/15/2019 |          24.1 |          3 |          1 |
|          2 | A         | Some other text | 3/2/2019  |          35.3 |          4 |          2 |
|          3 | B         | nan             | 1/1/2018  |          42.8 |          5 |          3 |


|   __rowidx | site_id   |   temperature | message         | day        |   __lineno |   __rowidx |
|-----------:|:----------|--------------:|:----------------|:-----------|-----------:|-----------:|
|          1 | B         |          42.1 | Some new text   | 01/01/2018 |          8 |          1 |
|          2 | A         |          35.3 | Some other text | 03/02/2019 |         10 |          2 |
|          3 | C         |          24.1 | Some text       | 09/15/2019 |         11 |          3 |




```json
{
    "header_pos": 0,
    "index": "site_id"
}
```


| site_id   | message         | date      |   temperature |   __lineno |   __rowidx |
|:----------|:----------------|:----------|--------------:|-----------:|-----------:|
| A         | Some other text | 3/2/2019  |          35.3 |          4 |          2 |
| B         | nan             | 1/1/2018  |          42.8 |          5 |          3 |
| C         | Some text       | 8/15/2019 |          24.1 |          3 |          1 |


| site_id   |   temperature | message         | day        |   __lineno |   __rowidx |
|:----------|--------------:|:----------------|:-----------|-----------:|-----------:|
| A         |          35.3 | Some other text | 03/02/2019 |         10 |          2 |
| B         |          42.1 | Some new text   | 01/01/2018 |          8 |          1 |
| C         |          24.1 | Some text       | 09/15/2019 |         11 |          3 |




```json
{
    "header_pos": 0,
    "index": "lineno"
}
```


|   __lineno | site_id   | message         | date      |   temperature |   __lineno |   __rowidx |
|-----------:|:----------|:----------------|:----------|--------------:|-----------:|-----------:|
|          3 | C         | Some text       | 8/15/2019 |          24.1 |          3 |          1 |
|          4 | A         | Some other text | 3/2/2019  |          35.3 |          4 |          2 |
|          5 | B         | nan             | 1/1/2018  |          42.8 |          5 |          3 |


|   __lineno | site_id   |   temperature | message         | day        |   __lineno |   __rowidx |
|-----------:|:----------|--------------:|:----------------|:-----------|-----------:|-----------:|
|          8 | B         |          42.1 | Some new text   | 01/01/2018 |          8 |          1 |
|         10 | A         |          35.3 | Some other text | 03/02/2019 |         10 |          2 |
|         11 | C         |          24.1 | Some text       | 09/15/2019 |         11 |          3 |



#### Matching columns with different names

From the change summary, we see that the two columns `date` and `day` appear as detected as `DELETED` and `ADDED` respectively.

We know that the two columns are actually the same column appearing with different names in the sources, so we can set the `column_renames` value using a `dict` to match the column names used for comparison.

!!! detail
    The order of the mapping (i.e. turning `day` into `date`, or viceversa) is not relevant, as the original names are in any case stored and compared as column metadata.

```py
class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
        'index': 'site_id',
        'column_renames': {'day': 'date'},
    }
```

After running `dacman`, the change percentage is lower, since the `date` column doesn't appear twice under different names:


```txt
percent change: 55.56%
             frac_changed  n_added  n_changed  n_deleted  n_modified  \
name                                                                   
message          0.333333        1          1          0           0   
date             1.000000        0          3          0           3   
temperature      0.333333        0          1          0           1   

             n_unchanged    status  
name                                
message                2  MODIFIED  
date                   0  MODIFIED  
temperature            2  MODIFIED  
```



From the complete output, we can verify that the column name obtained from the header (under the metadata property `name_header`) is changed:


```json
{
    "status": "MODIFIED",
    "metadata": {
        "common": {
            "name": "date",
            "dtype": "object"
        },
        "changes": {
            "name_header": {
                "a": "date",
                "b": "day"
            },
            "colidx": {
                "a": 2,
                "b": 3
            }
        }
    },
    "values": {
        "n_unchanged": 0,
        "n_added": 0,
        "n_deleted": 0,
        "n_modified": 3,
        "n_changed": 3,
        "frac_changed": 1.0
    }
}
```



#### Using value-specific data types instead of text

Despite matching the `date` column across both sources correctly,
all values in the `date` column still appear as modified.

We can get more details from the `values_by_column` section of the complete output, by comparing the entries under the `a` and `b` keys for each value.
We can see that only one of the values is actually modified,
while the others refer to the same date in both sources, but stored as text differently.


```json
{
    "UNCHANGED": {
        "count": 0
    },
    "ADDED": {
        "count": 0,
        "values": []
    },
    "DELETED": {
        "count": 0,
        "values": []
    },
    "MODIFIED": {
        "count": 3,
        "values": [
            {
                "a": {
                    "original": "3/2/2019",
                    "calculated_as": "3/2/2019",
                    "loc": {
                        "line": 4
                    }
                },
                "b": {
                    "original": "03/02/2019",
                    "calculated_as": "03/02/2019",
                    "loc": {
                        "lineno": 10,
                        "colidx": {
                            "a": 2,
                            "b": 3
                        },
                        "colname": {
                            "a": "date",
                            "b": "day"
                        }
                    }
                },
                "delta": NaN
            },
            {
                "a": {
                    "original": "1/1/2018",
                    "calculated_as": "1/1/2018",
                    "loc": {
                        "line": 5
                    }
                },
                "b": {
                    "original": "01/01/2018",
                    "calculated_as": "01/01/2018",
                    "loc": {
                        "lineno": 8,
                        "colidx": {
                            "a": 2,
                            "b": 3
                        },
                        "colname": {
                            "a": "date",
                            "b": "day"
                        }
                    }
                },
                "delta": NaN
            },
            {
                "a": {
                    "original": "8/15/2019",
                    "calculated_as": "8/15/2019",
                    "loc": {
                        "line": 3
                    }
                },
                "b": {
                    "original": "09/15/2019",
                    "calculated_as": "09/15/2019",
                    "loc": {
                        "lineno": 11,
                        "colidx": {
                            "a": 2,
                            "b": 3
                        },
                        "colname": {
                            "a": "date",
                            "b": "day"
                        }
                    }
                },
                "delta": NaN
            }
        ]
    }
}
```



By comparing the `date` values as actual `datetime` objects, rather than text,
we can address these false positives caused by the different date format.

By setting the `dtype` option to `True`, Dac-Man will attempt to convert values
from text to more specific data types (`datetime` or numeric) automatically.
This relies on pandas's robust data converter functionality,
and should work without needing further manual adjustments in most cases.

```py
class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
        'index': 'site_id',
        'column_renames': {'day': 'date'},
        'dtype': True
    }
```

After running `dacman` again, the result is:


```txt
percent change: 33.33%
             frac_changed  n_added  n_changed  n_deleted  n_modified  \
name                                                                   
message          0.333333        1          1          0           0   
date             0.333333        0          1          0           1   
temperature      0.333333        0          1          0           1   

             n_unchanged    status  
name                                
message                2  MODIFIED  
date                   2  MODIFIED  
temperature            2  MODIFIED  
```



We can observe the effect of the data type conversion
by comparing the `values_by_column` section for the `date` column with the result from the previous run:

- The two values representing the same dates are classified as `UNCHANGED` rather than `MODIFIED`
- For the value that was actually different,
  it is now possible to calculate the delta between the two sources expressed as a meaningful quantity:
  in this case, since the values are of type `datetime`, `delta` is of type `timedelta`


```json
{
    "UNCHANGED": {
        "count": 2
    },
    "ADDED": {
        "count": 0,
        "values": []
    },
    "DELETED": {
        "count": 0,
        "values": []
    },
    "MODIFIED": {
        "count": 1,
        "values": [
            {
                "a": {
                    "original": "8/15/2019",
                    "calculated_as": "2019-08-15 00:00:00",
                    "loc": {
                        "line": 3
                    }
                },
                "b": {
                    "original": "09/15/2019",
                    "calculated_as": "2019-09-15 00:00:00",
                    "loc": {
                        "lineno": 11,
                        "colidx": {
                            "a": 2,
                            "b": 3
                        },
                        "colname": {
                            "a": "date",
                            "b": "day"
                        }
                    }
                },
                "delta": "-31 days +00:00:00"
            }
        ]
    }
}
```



Since the data type conversion was applied automatically, `delta`s are available for all columns with numeric values,
such as `temperature`:


```json
{
    "UNCHANGED": {
        "count": 2
    },
    "ADDED": {
        "count": 0,
        "values": []
    },
    "DELETED": {
        "count": 0,
        "values": []
    },
    "MODIFIED": {
        "count": 1,
        "values": [
            {
                "a": {
                    "original": "42.8",
                    "calculated_as": 42.8,
                    "loc": {
                        "line": 5
                    }
                },
                "b": {
                    "original": "42.1",
                    "calculated_as": 42.1,
                    "loc": {
                        "lineno": 8,
                        "colidx": {
                            "a": 3,
                            "b": 1
                        },
                        "colname": {
                            "a": "temperature",
                            "b": "temperature"
                        }
                    }
                },
                "delta": 0.6999999999999957
            }
        ]
    }
}
```


