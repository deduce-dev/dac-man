# Extending the CSV plug-in

This example illustrates how to implement a change analysis for CSV files
tailored to specific features of the data being analyzed,
by creating a minimal extension of the included CSV plug-in.

A complete runnable version of the entire script is available at the end of this section,
and in the [`examples/csv`](https://github.com/deduce-dev/dac-man/blob/master/examples/csv/) directory of the Dac-Man source code repository,
together with the example data shown below as two separate CSV files.

## Creating the `main` block of the change analysis script

We start from creating the skeleton of the analysis script in a Python file, e.g. `/home/user/my_csv_ana.py`.
The first line starting with `#!...` is necessary to make the script executable.

Dac-Man analysis scripts must accept two command-line arguments,
which are the paths to the files that will be compared.

```py
#!/usr/bin/env python3

import sys

if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    file_a, file_b = cli_args[0], cli_args[1]
```

## Implementing the change analysis with Dac-Man's API

Then, we create a Python function, having the two files as arguments,
implementing the custom change analysis using Dac-Man's API.
This will allow us to integrate our customized comparator class
while reusing much of the functionality provided by Dac-Man.

```py
import sys

import dacman

def run_my_change_analysis(file_a, file_b):
    comparisons = [(file_a, file_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    file_a, file_b = cli_args[0], cli_args[1]
    run_my_change_analysis(file_a, file_b)
```

## Creating a specialized comparator class

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

In the following, we'll build an extension of the CSV plug-in tailored to the structure of this source data,
and how to integrate it in a custom analysis script.

We start from creating the comparator subclass implementing our customizations by extending the `CSVPlugin` class:

```py
from dacman.plugins.csv import CSVPlugin

class MyCSVPlugin(CSVPlugin):
    pass
```

### Setting column names from the header

Our first step to adapt the `MyCSVPlugin` to the input data is specifying the position of the row containing the header,
from which the table column names will be obtained.

This is done by setting the value of `header_pos` in the `calc_options` plug-in attribute, which will be zero since the header is the first row (starting from 0) in both sources:

```py
class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
    }
```

### Setting the index

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

### Matching columns with different names

In the input data, the two columns `date` in `A.csv` and `day` in `B.csv` refer to the same data.
Since their name is different in the two version,
they will be detected as:

- `date`: `DELETED` from `A.csv`, because it only appears in the first file;
- `day`: `ADDED` to `B.csv`, because it only appears in the second file.

We know that the two columns are actually the same column appearing with different names in the sources, so we can set the `column_renames` value using a `dict` to match the column names used for comparison.

```py
class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
        'index': 'site_id',
        'column_renames': {'day': 'date'},
    }
```

!!! detail
    The order of the mapping (i.e. turning `day` into `date`, or the other way around) is not relevant, as the original names are in any case stored and compared as column metadata.

### Using value-specific data types instead of text

Despite matching the `date` column across both sources correctly,
all values in the `date` column will be interpreted as modified.
This is because the text values representing the same dates
are expressed as text in different formats.

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

## Integrating our custom comparator in the change analysis

The next step is to add the code for our custom comparator class `MyCSVPlugin`
and set it as the plug-in to use for the comparison:

```py
import sys

import dacman
from dacman.plugins.csv import CSVPlugin


class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
        'index': 'site_id',
        'column_renames': {'day': 'date'},
        'dtype': True
    }


def run_my_change_analysis(file_a, file_b):
    comparisons = [(file_a, file_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(MyCSVPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    file_a, file_b = cli_args[0], cli_args[1]
    run_my_change_analysis(file_a, file_b)
```

## Running the custom change analysis

The complete code for this custom analysis script is:

```py
#!/usr/bin/env python3

import sys

import dacman
from dacman.plugins.csv import CSVPlugin


class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
        'index': 'site_id',
        'column_renames': {'day': 'date'},
        'dtype': True
    }


def run_my_change_analysis(file_a, file_b):
    comparisons = [(file_a, file_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(MyCSVPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    file_a, file_b = cli_args[0], cli_args[1]
    run_my_change_analysis(file_a, file_b)
```

To test this change analysis script with Dac-Man,
add executable permissions to the `my_csv_ana.py` Python file using e.g. the `chmod` command:

```sh
chmod +x /home/user/my_csv_ana.py
```

Then, navigate to the `examples/csv` directories and run:

```sh
dacman diff A.csv B.csv --script /home/user/my_csv_ana.py
```

!!! tip
    A complete runnable copy of this file is already available as [`examples/csv/my_csv_ana.py`](https://github.com/deduce-dev/dac-man/blob/master/examples/csv/my_csv_ana.py)
