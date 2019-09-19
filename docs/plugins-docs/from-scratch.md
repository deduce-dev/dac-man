# Writing a Dac-Man plug-in from scratch

This example will illustrate how to create a Dac-Man plug-in from scratch to analyze changes in files of arbitrary type and structure.

!!! example
    A ready-to-use script for this example can be found under [`examples/scripts/matrix_change_ana.py`](https://github.com/dghoshal-lbl/dac-man/blob/master/examples/scripts/matrix_change_ana.py).

## Overview

The goal of the example change analysis is to detect and quantify changes in datasets composed of files of a specialized type.
Each file contains one 2D matrix with numeric (float) values, saved as text.

We want to compare two datasets, stored as directories `dataset-v1` and `dataset-v2`, to obtain the following information:

- How many files were added, deleted, modified between the two datasets
- For files that were modified, calculate a custom change metric quantifying, if possible,
  the amount of changes between the two matrices stored in the two files

Dac-Man's API already provide all the functionality needed to perform directory-level comparison between the datasets.
All the users have to implement is:

- A simple custom analysis script using Dac-Man's API
- A specialized plug-in class, that will be used by Dac-Man to compare files that have been detected as modified
- A specialized Adaptor class, converting data from the specific file format under study to a Dac-Man Record

## Creating a custom analysis script

We start from creating a Python file, e.g. `/home/user/matrix_change_ana.py`.

The first line of the file should contain the `#!...` line needed to later use the file as an executable.
Below it, we add the `import` statements for the modules that we'll use in the script:

```py
#!/usr/bin/env python3
import sys

import dacman
from dacman.compare import base
from dacman.compare.adaptor import DacmanRecord

import numpy
import numpy.linalg
```

Dac-Man change analysis scripts should accept two arguments, the paths to the files that should be compared.
We read these from the command-line arguments, and pass them to the `run_matrix_change_ana()` function:

```py
#!/usr/bin/env python3
import sys

import dacman
from dacman.compare import base
from dacman.compare.adaptor import DacmanRecord

import numpy
import numpy.linalg


def run_matrix_change_ana(*args):
    ...


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    path_a, path_b = cli_args[0], cli_args[1]
    run_matrix_change_ana(path_a, path_b)
```

The `run_matrix_change_ana()` function uses Dac-Man's API to perform the comparison between the input sources,
which are passed to it as arguments:

```py
#!/usr/bin/env python3
import sys

import dacman
from dacman.compare import base
from dacman.compare.adaptor import DacmanRecord

import numpy
import numpy.linalg


... # custom plug-in code goes here


def run_matrix_change_ana(path_a, path_b):
    comparisons = [(path_a, path_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(...)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    path_a, path_b = cli_args[0], cli_args[1]
    run_matrix_change_ana(path_a, path_b)
```

The `use_plugin()` method of the `DataDiffer` object allows us to specify a specialized plug-in to perform the comparison.

In the next part, we'll see how to implement everything needed for our custom change analysis using a custom Dac-Man plug-in.

## Creating a specialized plug-in

At the basis of a Dac-Man plug-in is the Comparator class,
managing all the steps needed for comparing a single pair of files (one from each dataset) that have been modified.

In the same file, above the `run_matrix_change_analysis()`, we start adding the code for our custom plug-in `MatrixTxtPlugin`.

Dac-Man plug-ins should inherit from the `dacman.compare.base.Comparator` abstract base class,
and implement the `description()`, `supports()`, and `compare()` methods (described here) as well as the `percent_change()` and `stats()` methods (described later in this document).

The `compare()` method takes at least two arguments, the paths of the files being compared.
The rest of the implementation is left free to the users to customize according to their specific needs.

```py
#!/usr/bin/env python3
import sys

import dacman
from dacman.compare import base
from dacman.compare.adaptor import DacmanRecord

import numpy
import numpy.linalg


class MatrixTxtPlugin(base.Comparator):

    @staticmethod
    def description():
        return "A Dac-Man plug-in to compare matrices saved as text files"

    @staticmethod
    def supports():
        return ['txt']

    def compare(self, path_a, path_b, *args):
        pass


# rest of the script
def run_matrix_change_ana(path_a, path_b):
    ...

```

### Creating Dacman Records from sources

The first step to implement the `compare()` function is to create Dac-Man records from the input sources.
Since we use the same steps to create a record for both files, we group those steps to a separate helper method, `get_record()`:

```py
from dacman.compare.adaptor import DacmanRecord


class MatrixTxtPlugin(base.Comparator):

    def get_record(self, path):
        return DacmanRecord(path)

    def compare(self, path_a, path_b, *args):
        rec_a = self.get_record(path_a)
        rec_b = self.get_record(path_b)
```

At this point, however, the `DacmanRecord` objects are not yet capable of supporting our specific file format.
We enable this by creating a specialized Adaptor class.

### Creating an Adaptor for a custom file format

The purpose of a Adaptor is to convert an arbitrary data source to a Dac-Man Record,
which in turn exposes a common interface allowing the data to be compared in a structured way.

We begin from creating an Adaptor class for the format used by our datasets.
Specialized Adaptor class should inherit from the `dacman.compare.base.DacmanRecordAdaptor` abstract base class,
and implement the `transform()` method.

The `transform()` method takes a single argument, the path of the data file,
and return a tuple of 2 values, each of which a sequence storing the content of the headers and the data of the file respectively.

```py
from dacman.compare import base


class MatrixTxtAdaptor(base.DacmanRecordAdaptor):

    def transform(self, data_path):
        headers = []
        data = []
        return headers, data
```

We use the `numpy.loadtxt()` function to load the data into a numpy array:

```py
from dacman.compare import base
import numpy


class MatrixTxtAdaptor(base.DacmanRecordAdaptor):

    def transform(self, data_path):
        headers = []
        data = numpy.loadtxt(data_path)

        return headers, data
```

### Enabling support for custom file formats in Dac-Man Records

Now that our specialized `MatrixTxtAdaptor` class is complete,
we use it to enable support for our custom file format to Dac-Man Records in our plug-in.

In the `get_record()` method of our `MatrixTxtPlugin` class,
we pass all necessary information about the custom file format to the DacmanRecord object,
such as which Adaptor to use and which file extensions are supported.

After that, the `DacmanRecord` object will be able to transform the source correctly.

```py
class MatrixTxtAdaptor(base.DacmanRecordAdaptor):

    def transform(self, data_path):
        headers = []
        data = numpy.loadtxt(data_path)

        return headers, data


class MatrixTxtPlugin(base.Comparator):

    def get_record(self, path):
        ext = 'txt'

        rec = DacmanRecord(path)

        rec.file_support = {ext: True}
        rec.lib_support = {ext: 'numpy'}
        rec.file_adaptors = {ext: MatrixTxtAdaptor}

        rec._transform_source()

        return rec
    ...
```

### Implementing specialized change metrics calculations for matrices

Thanks to the specialized `MatrixTxtAdaptor`, we know that the matrix data contained in each source file
is a 2D numpy array, accessible through the `.data` attribute of each `DacmanRecord` object.
This allows us to leverage available tools supporting numpy arrays to implement our calculations very efficiently.

We factor out all calculations to a separate method of the plug-in, `get_matrix_change_metrics()`,
taking as arguments the two Dac-Man Records, and returning a dictionary containing the change metrics.

We also add a `threshold` parameter to the plug-in, used to specify
the minimum (absolute) difference that two corresponding values from each matrix should have to be considered "changed".

```py
import numpy
import numpy.linalg


class MatrixTxtPlugin(base.Comparator):

    threshold = 0.001

...

    def get_matrix_change_metrics(self, rec_a, rec_b):
        mat_a = rec_a.data
        mat_b = rec_b.data

        mat_delta = mat_a - mat_b

        n_values_over_threshold = numpy.sum(numpy.abs(mat_delta) > self.threshold)
        frac_changed = n_values_over_threshold / mat_delta.size

        sum_of_delta = numpy.sum(mat_delta)
        mean_of_delta = numpy.mean(mat_delta)
        norm_of_delta = numpy.linalg.norm(mat_delta)

        delta_max = numpy.max(mat_a) - numpy.max(mat_b)
        delta_min = numpy.min(mat_a) - numpy.min(mat_b)

        return {
            'frac_changed': frac_changed,
            'sum(A - B)': sum_of_delta,
            'mean(A - B)': mean_of_delta,
            'norm(A - B)': norm_of_delta,
            'delta(max(A) - max(B))': delta_max,
            'delta(min(A) - min(B))': delta_min,
        }
```

Then, we integrate these change metrics into the comparison by calling the function in the `compare()` method.
We wrap the call to the `get_matrix_change_metrics()` method in a `try/except` statement
to catch errors that can potentially occur during the calculations, and store the error message.

```py
class MatrixTxtPlugin(base.Comparator):

    def compare(self, path_a, path_b, *args):
        rec_a = self.get_record(path_a)
        rec_b = self.get_record(path_b)

        try:
            self.metrics = self.get_matrix_change_metrics(rec_a, rec_b)
        except Exception as e:
            self.metrics = {'error': str(e)}

        return self.metrics
```

### Adding methods for output

Finally, we implement the methods `percent_change()` and `stats()`,
used to access information about the amount of change expressed as a single value,
and more detailed information about the changes in the files being compared.

The choice of how to express these is left to the users.
For this example, we use the previously calculated `frac_changed` for `percent_change()`,
and print the results of the change metrics calculations in its entirety:

```py
class MatrixTxtPlugin(base.Comparator):
...

    def percent_change(self):
        frac = self.metrics.get('frac_changed', 0)
        return frac * 100

    def stats(self, changes):
        print(changes)
```

### Integrating the plug-in in the custom change analysis

At this point, the only thing left to do is integrating our specialized plug-in into Dac-Man's processing pipeline.

In the `run_matrix_change_ana()` function, we specify `MatrixTxtPlugin` as the plug-in to use in the `use_plugin()` method of the `DataDiffer` object:

```py
#!/usr/bin/env python3
import sys

import dacman
from dacman.compare import base
from dacman.compare.adaptor import DacmanRecord

import numpy
import numpy.linalg


class MatrixTxtPlugin(base.Comparator):
    ... # rest of the plug-in code


def run_matrix_change_ana(path_a, path_b):
    comparisons = [(path_a, path_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(MatrixTxtPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    path_a, path_b = cli_args[0], cli_args[1]
    run_matrix_change_ana(path_a, path_b)
```

## Complete change analysis script

The complete code for this change analysis script is:

```py
#!/usr/bin/env python3
import sys

import dacman
from dacman.compare import base
from dacman.compare.adaptor import DacmanRecord

import numpy
import numpy.linalg


class MatrixTxtAdaptor(base.DacmanRecordAdaptor):

    def transform(self, data_path):
        headers = []
        data = numpy.loadtxt(data_path)

        return headers, data


class MatrixTxtPlugin(base.Comparator):

    threshold = 0.01

    @staticmethod
    def description():
        return "A Dac-Man plug-in to compare matrices saved as text files"

    @staticmethod
    def supports():
        return ['txt']

    def get_record(self, path):
        ext = 'txt'

        rec = DacmanRecord(path)

        rec.file_support = {ext: True}
        rec.lib_support = {ext: 'numpy'}
        rec.file_adaptors = {ext: MatrixTxtAdaptor}

        rec._transform_source()

        return rec

    def compare(self, path_a, path_b, *args):
        rec_a = self.get_record(path_a)
        rec_b = self.get_record(path_b)

        try:
            self.metrics = self.get_matrix_change_metrics(rec_a, rec_b)
        except Exception as e:
            self.metrics = {'error': str(e)}

        return self.metrics

    def get_matrix_change_metrics(self, rec_a, rec_b):
        mat_a = rec_a.data
        mat_b = rec_b.data

        mat_delta = mat_a - mat_b

        n_values_over_threshold = numpy.sum(numpy.abs(mat_delta) > self.threshold)
        frac_changed = n_values_over_threshold / mat_delta.size

        sum_of_delta = numpy.sum(mat_delta)
        mean_of_delta = numpy.mean(mat_delta)
        norm_of_delta = numpy.linalg.norm(mat_delta)

        delta_max = numpy.max(mat_a) - numpy.max(mat_b)
        delta_min = numpy.min(mat_a) - numpy.min(mat_b)

        return {
            'frac_changed': frac_changed,
            'sum(A - B)': sum_of_delta,
            'mean(A - B)': mean_of_delta,
            'norm(A - B)': norm_of_delta,
            'delta(max(A) - max(B))': delta_max,
            'delta(min(A) - min(B))': delta_min,
        }

    def percent_change(self):
        frac = self.metrics.get('frac_changed', 0)
        return frac * 100

    def stats(self, changes):
        print(changes)


def run_matrix_change_ana(path_a, path_b):
    comparisons = [(path_a, path_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(MatrixTxtPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    path_a, path_b = cli_args[0], cli_args[1]
    run_matrix_change_ana(path_a, path_b)
```

## Running the change analysis

First, make the `/home/user/matrix_change_ana.py` file executable by using e.g. the `chmod` command:

```sh
chmod +x /home/user/matrix_change_ana.py
```

!!! example
    A ready-to-use script for this example can be found under [`examples/scripts/matrix_change_ana.py`](https://github.com/dghoshal-lbl/dac-man/blob/master/examples/scripts/matrix_change_ana.py).

Then, to run the change analysis on two version of an example dataset,
navigate to the `example/data/matrix_txt` directory and run:

```sh
dacman diff --datachange dataset-v1 dataset-v2 --script /home/user/matrix_change_ana.py
```
