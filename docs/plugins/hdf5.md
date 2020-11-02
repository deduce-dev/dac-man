# The Dac-Man HDF5 Plug-in

The Dac-Man HDF5 plug-in compares HDF5 files using metadata information collected from the Objects contained in the file.

## Key Concepts

!!! note
    To reduce ambiguities, capitalized nouns (Object, Dataset, Group, Attribute, File, etc) are used when referring to HDF5 data types or concepts.

The operation of the plug-in can be summarized in these steps:

- Access Objects contained in input Files, descending recursively through the complete structure
- Collect metadata for each Object, for a set of properties that depends on its type
- For each file, store the metadata items as a Record, using one of the metadata properties as the index key
- Generate comparison pairs from the two Records, associating Objects in each Record with the same key
- For each comparison pair, calculate and store change metrics by comparing corresponding properties for the pair's Objects
- Process the accumulated Object-level change metrics to calculate aggregated statistics for the File-level comparison

### Metadata Properties and Change Metrics

This is a list of the types of change that are detected by the plug-in,
which in turn corresponds to one or more metadata properties of the two Objects being compared.
Since the metadata properties collected from each Object depend on the Object's type, the change metrics collected for the comparison pair will depend on the subset of properties common to both Objects.
In general, the more similar the two Objects are,
the more specific the change metrics collected when comparing them will be.

Whenever possible, the nomenclature is consistent with the `h5py` API.

#### Between generic h5 Objects

- `type_h5`: the two Objects have different HDF5 types
- `attributes`: the attributes of each of the two Objects are different. Changes in `attributes` are orthogonal to `type_h5`, i.e. either property can change independently from the other

#### Between Datasets

- `ndim`: the two Datasets have different number of dimensions (axes)
- `shape`: the two Datasets have different dimensions. `shape` is a tuple of integers where `len(shape)` = `ndim`: therefore, two arrays can have the same `ndim`, but different `shape`
- `dtype`: the two Datasets have different data types. Changes in `dtype` are orthogonal to differences in structure (`ndim`, `shape`).
- `value`: the content of the two Datasets is different. For a more specialized comparison of `value`, `ndim`, `shape`, and `dtype` must be equal

#### Between Groups

*Note: in `h5py`, `File` objects are also `Group`s.*

- `num_objs`: the two Groups contain different number of Objects. Only direct children are considered (i.e. the content of sub-Groups is excluded). Both the total Object count and counts by `type_h5` are included: e.g. `num_objs: {Dataset: 3, Group: 2, total: 5}`

#### Between Files

- `filename`: the two Files have different paths on the filesystem

## Usage

### Requirements

The `h5py` Python package is required as an additional dependency.

!!! tip
    These [instructions](../../install/dependencies) describe how to install dependencies for all of Dac-Man's included plug-ins in a single step.

### Using the HDF5 Plug-in

As part of the included Dac-Man plug-ins, once its dependencies have been installed,
the HDF5 plug-in will be used by default when comparing HDF5 files.

The [`examples/plugin_test/`](https://github.com/deduce-dev/dac-man/blob/master/examples/plugin_test/) directory of the Dac-Man source code repository
contains two example HDF5 files in the two sub-directories `v0` and `v1`.
To compare these example files, navigate to the `examples/plugin_test` directory
and run `dacman diff` with the `--datachange` option:

```sh
cd examples/plugin_test
dacman diff v0 v1 --datachange
```

## API

### Changing the indexing of the comparison pairs

By default, the plug-in uses the `name` property (corresponding to the `Object.name` attribute in `h5py`) as the comparison pair index,
i.e. the key used to select corresponding Objects from each input File and associate them for the pairwise comparison.

There can be circumstances where the Object name is not unique or is not the most representative property for a particular file structure,
e.g. if Datasets have a `uid` Attribute representing a unique ID that is the same in both Files.

For these cases, it's possible to customize the creation of the Record index
by creating a subclass of `HDF5Plugin` and overriding the `record_key_getter` staticmethod:

```py
class UIDDatasetPlugin(HDF5Plugin):

    @staticmethod
    def record_key_getter(metadata):
        if metadata['type_h5'] == h5py.Dataset:
            return metadata['attributes']['uid']
        return metadata['name']
```
