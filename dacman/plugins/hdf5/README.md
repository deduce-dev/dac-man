# HDF5 Plug-in

A Dac-man plug-in to compare HDF5 files, using information from metadata collected from the contained Objects.

## Principles

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
In general, more specific metrics are possible the more similar the two Objects are.

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

- `num_objs`: the two Groups contain different number of Objects. Only direct children (i.e. the content of sub-Groups is excluded) are considered. Both the total Object count and counts by `type_h5` are included: e.g. `num_objs: {Dataset: 3, Group: 2, total: 5}`

#### Between Files

- `filename`: the two Files have different paths on the filesystem

## Usage

### Dependencies

Similarly to Dac-Man, the `hdf5` plug-in is compatible with Python 3.6+.
In addition, the `h5py` Python package is required.

### Using the HDF5 Plug-in

### From the command line (standalone mode)

After installing Dac-Man and `h5py`, run:

```sh
python -m dacman.plugins.hdf5 A.h5 B.h5
```

where `A.h5` and `B.h5` are the two HDF5 files to compare.

Use the `--help` flag for a complete list of command-line options:

```sh
python -m dacman.plugins.hdf5 --help
```

## Customizing the Plug-in

The capability of HDF5 files of storing arbitrary data within a complex structure means that the types of possible comparisons is effectively unlimited.
Rather than trying to anticipate all possible use cases, the plug-in is designed so that it is possible for users to modify the default behavior, and extend it with more specialized functionality.
In this section, a few cases are given as examples.

### Add specialized comparisons for Datasets

A common use case would be to add a comparison for a specialized type of Dataset.
The additional functionality can be added by minimally extending the main classes involved in the comparison processing chain.

For this example, we can consider the case of comparing images stored in an HDF5 files in the EDF format by analyzing changes in the mean luminance and number of unique values.

#### Collecting metadata

```py
def collect_from_edf(d, dataset):
    image = dataset[...]

    d['mean_lumi'] = numpy.mean(image)
    d['n_unique'] = numpy.unique(image)


class MyMetadataCollector(MetadataCollector):

    @property
    def is_image_edf(self):
        return self.is_dataset and self.obj.name.endswith('.edf')

    def collect(self):
        super().collect()

        if self.is_image_edf:
            self['image_edf'] = {}
            collect_from_edf(self['image_edf'], self.obj)
```

#### Calculating comparison metrics

```py
class MyMetrics(ObjMetadataMetrics):

    @property
    def is_image_edf(self):
        return 'image_edf' in self.properties

    def calculate(self):
        super().calculate()

        if self.is_image_edf:
            if change_in('image_edf'):
                val_a, val_b = self.get_values('image_edf', orient=tuple)
                self['delta_mean_lumi'] = val_a['mean_lumi'] - val_b['mean_lumi']
                self['delta_n_unique'] = val_a['n_unique'] - val_b['n_unique']
```

#### Creating custom plug-in

```py
class MyPlugin(HDF5PLugin):

    def get_collector(self, **kwargs):
        return MyMetadataCollector(**kwargs)

    def get_metrics(self, **kwargs):
        return MyMetrics(**kwargs)
```

### Elementwise comparison between Attributes

Even though in the current implementation Attributes are compared as a single item, it is possible to perform a more granular comparison.
Attributes in HDF5 are mappings between text keys and values, where values can be of any supported data type.
Effectively, for the purpose of a comparison, Attributes can be considered a flat Group (i.e. no sub-groups) with one or more Datasets.
Therefore, comparisons between Attributes has similar semantics to comparison between Groups:

- Attribute keys can be present in only one of the Objects being compared; in both and values are equal; or in both and values are different
- For Attribute values, the types of change are the same as for Datasets

### Changing the indexing of the comparison pairs

By default, the plug-in uses the `name` property (corresponding to the `Object.name` attribute in `h5py`) as the comparison pair index,
i.e. the key used to select corresponding Objects from each input File and associate them for the pairwise comparison.

There can be circumstances where the Object name is not unique or is not the most  representative property for a particular file structure, e.g. if Datasets have a `uid` Attribute representing a unique ID that is the same in both Files.

For these cases, it's possible to customize the creation of the Record index by passing a custom function through the `key_getter` parameter:

```py
def uid_key_getter(metadata):
    return metadata['attributes']['uid']
```

And, in a subclass of `HDF5Plugin`:

```py
def get_record(self, file, **kwargs):
    ...
    return Record(obj, key_getter=uid_key_getter)
```
