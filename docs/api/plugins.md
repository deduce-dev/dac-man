# The Dac-Man Plug-ins API

The plug-ins in Dac-Man are different 'comparators' that capture changes in files and datasets.
All the comparator plug-ins registered to Dac-Man are derived from the base `Comparator` class.

## `Comparator` class

The `Comparator` class is an abstract class that provides the underlying methods
for defining the metadata and algorithm for capturing data changes.
All the methods in this class are abstract and need to be implemented by the derived plug-in class.

#### `supports()`

A static method returning the file/data types that are supported by the specific plug-in.

#### `description()`

A static method that describes the specific plug-in.

#### `compare(a, b, *args)`

The core method for implementing the algorithm to compare two files/datasets.

#### `percent_change()`

Method to summarize the amount of change in two files with respect to the comparison algorithm.

#### `stats(changes)`

Method for providing statistics on calculated changes from the `compare` method.

## Creating Plug-ins

In order to create and register plug-ins, users need to implement the methods
in the `Comparator` class.
Users can either choose to add multiple plug-ins in a single module,
or create a module for each plug-in.

The following example shows a module for each plug-in (`single_plugin.py`):

```py
class MyPlugin(Comparator):
  def supports():
    ...
  ...
  def compare(a, b, *args):
    ...
  ...
```

The following example shows multiple plug-ins in a module (`multiple_plugins.py`):

```py
class TxtPlugin(Comparator):
  def supports():
    return ['txt']
  ...
  def compare(a, b, *args):
    ...
  ...


class CSVPlugin(Comparator):
  def supports():
    return ['csv']
  ...
  def compare(a, b, *args):
    ...
  ...
```
