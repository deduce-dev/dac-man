# Extending the JSON plug-in

The following example illustrates how to implement a change analysis for JSON
files tailored to specific features of the data being analyzed,
by creating a minimal extension of the included JSON plug-in
with a more detailed output.

A complete runnable version of the entire script is available at the end of this section,
and in the [`examples/json`](https://github.com/deduce-dev/dac-man/blob/master/examples/json/)
directory of the Dac-Man source code repository,
together with the example data (shown immediately below) as two separate json files.

## Test data

In this example, we perform an analysis of the changes between the files `a.json` and `b.json`:

`a.json`
```py
{
   "name": "John Doe",
   "age": "30",
   "cars": {
      "car1": {
         "brand": "Ford",
         "color":  "white"
      }
   }
}
```

`b.json`
```
{
   "age": "33",
   "name": "Jane Doe",
   "cars": {
      "car1": {
         "brand": "",
         "color":  "black"
      },
      "car2": {
         "brand": "Tesla",
         "color": "white"
      }
   },
   "pets": {}
}
```

The example files contain few lines, allowing us to visually inspect the
differences.
- `b.json` contains an additional key "pets"
- The values for name, age and, cars differ

## Creating a specialized comparator class

In the following, we'll build an extension of the JSON plug-in tailored to the
structure of this source data, and how to integrate it in a custom analysis script.
We begin by creating a comparator subclass implementing our customizations
by extending the `JSONPlugin` class:


```py
from dacman.plugins.json import JSONPlugin

class MyJSONPlugin(JSONPlugin):
    ...
```

### Setting the output detail level from the header
The only customization we are specifying here is varying the detail level
for the outputs of the JSON plug-in.

## Creating a runnable change analysis script

### Creating the `__main__` block

We start from creating the skeleton of the analysis script in a Python file,
for instance, `/home/user/my_json_analysis.py`.
Dac-Man analysis scripts are required to accept two command-line arguments,
where arguments are the file paths to be compared.

```py
import sys

if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    file_a, file_b = cli_args[0], cli_args[1]
```

### Implementing the change analysis with Dac-Man's API

Next, we create a Python function `run_my_change_analysis(file_a, file_b)`
taking in the two file paths as arguments,
and implementing the custom change analysis using Dac-Man's API.
This allows us to integrate our customized comparator class
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

### Integrating our custom comparator in the change analysis

The next step is to add the code for our custom comparator class `MyJSONPlugin`
and set it as the plug-in to use for the comparison:

```py
import sys
import dacman
from dacman.plugins.json import JSONPlugin


class MyJSONPlugin(JSONPlugin):
      output_options = {'detail_level': 2}


def run_my_change_analysis(file_a, file_b):
    comparisons = [(file_a, file_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(MyJSONPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    file_a, file_b = cli_args[0], cli_args[1]
    run_my_change_analysis(file_a, file_b)
```

### Making the change analysis script executable

Finally, we make the script executable by adding the "shebang" line at the top,
and using the `chmod` command to add executable permissions:

```py
#!/usr/bin/env python3
```

```sh
chmod +x /home/user/my_json_analysis.py
```

## Testing the custom change analysis

To test this change analysis with Dac-Man,
navigate to the `examples/json` directories and run:

```sh
dacman diff a.json b.json --script /home/user/my_json_analysis.py
```

!!! tip
    A runnable copy of this file is available in [`examples/json/my_json_analysis.py`](https://github.com/deduce-dev/dac-man/blob/master/examples/json/my_json_analysis.py)


### Final Output
The final output from executing the script above is as follows:

```sh
cli_args=['a.json', 'b.json']
[INFO] Sequentially comparing dataset pairs.
Data comparator plugin = MyJSONPlugin
[INFO] Comparing a.json and b.json using MyJSONPlugin

Contents in a.json denoted with "+"
Contents in b.json denoted with "-"


-  pets: {
-  }
+  name: John Doe
-  name: Jane Doe
  cars: {
-    car2: {
-      brand: Tesla
-      color: white
-    }
    car1: {
+      brand: Ford
-      brand:
+      color: white
-      color: black
    }
  }
+  age: 30
-  age: 33
[INFO] --- Using custom detail level 2

Level 0 detail:
        a.json has -66.67% less keys than b.json


Level 1 detail:
        Total number of keys in a.json: 6
        Total number of keys in b.json: 10
        Total number of overlapping keys in both files: 6


Level 2 detail:
        JSON level 0 has
                0 unique keys for a.json
                1 unique keys for b.json
                3 keys shared between files
        JSON level 1 has
                3 unique keys for b.json
                0 unique keys for a.json
                3 keys shared between files
[INFO] Data comparison complete.
```