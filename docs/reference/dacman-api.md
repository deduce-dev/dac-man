# The Dac-Man API

The top-level `dacman` module provides methods and classes for doing data comparisons at scale.
Data can be compared using `dacman.diff()`.

## `dacman.diff()`

```py
def dacman.diff(new_file, old_file, *argv, comparator_plugin=None)
```

Function to perform a single comparison using the specified plug-in.

## `dacman.DataDiffer`

```py
class dacman.DataDiffer(comparisons, executor=Executor.DEFAULT)
```

Class that compares multiple files or objects.
This class takes a list of comparisons and performs the comparisons in parallel.
The `executor` argument specifies the type of runtime to be used for doing the comparisons.

### `use_plugin(plugin)`

Method to set a specific plug-in for comparing the files.
If no plug-in is set, then Dac-Man will select one of the internal plug-ins based on file/data types.

### `start()`

Method to start the comparison using the specified runtime and plug-in.

### `mpi_communicator`

Attribute specifying the MPI communicator to be used when using the MPI executor.

## `dacman.Executor`

```py
class dacman.Executor()
```

Types of runtime in Dac-Man.

## `dacman.plugins`

```py
dacman.plugins.default.DefaultPlugin
```

Module containing the system and user-defined plug-in.
