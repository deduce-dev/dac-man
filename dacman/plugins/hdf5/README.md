# HDF5 Plug-in

A Dac-man plug-in to compare HDF5 files, using information from metadata collected from the contained Objects.

## Key Concepts

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

To install it, from the environment where Dac-Man is installed, run:

```sh
# install using Conda
conda install h5py

# or, alternatively, using pip
python -m pip install h5py
```

### Using the HDF5 Plug-in

As part of the core Dac-Man plug-ins, when analyzing changes in HDF5 files, the `hdf5` plug-in will be used by default.

To compare the two files `A.h5` and `B.h5`, after installing Dac-Man and `h5py`, run:

```sh
dacman diff A.h5 B.h5
```

## Extending the Plug-in

The capability of HDF5 files of storing arbitrary data within a complex structure means that the types of possible comparisons is effectively unlimited.
Rather than trying to anticipate all possible use cases, the plug-in is designed so that it is possible for users to modify the default behavior, and extend it with more specialized functionality.
In this section, a few cases are given as examples.

---

### Example use case: analyzing changes in EDF tomography data

A common use case would be to add a comparison for a specialized type of Dataset.
The additional functionality can be added by minimally extending the main classes involved in the change analysis chain.

As an example case study, we consider analyzing changes in images stored in HDF5 files in the EDF format.
The complete code for this example can be found in [`dacman/plugins/als_tomo.py`](https://github.com/dghoshal-lbl/dac-man/blob/feature/hdf5-plugin/dacman/plugins/als_tomo.py).

#### Installing extra dependencies

On top of the default Dac-Man dependencies and the `h5py` package required by the HDF5 plug-in, custom change analyses might require additional dependencies.

The `als_tomo` change analysis uses functions from the `numpy`, `scipy`, and `scikit-learn` Python modules.
To install them, from the environment where Dac-Man is installed, run:

```sh
# install packages using Conda
conda install numpy scipy scikit-learn

# or, alternatively, using pip
python -m pip install numpy scipy scikit-learn
```

#### Developing the extension

A brief walkthrough of the code for `als_tomo.py` is presented below.

##### Collecting metadata

The first step is to define how metadata will be collected from each Object in each input File.
For this, we create `ALSTomoMetadataCollector`, a subclass of `dacman.plugins.hdf5.metadata.MetadataCollector`.

Looking more in detail at its methods:

- The `is_edf_dataset` property is used to define which Datasets should be treated as EDF images.
  In the example, the name of the Dataset is used as the basis for the criteria, but other properties could be used as well, to e.g. select Datasets based on their shape or data type
- The `collect()` method defines how the metadata is collected depending on the characteristics of the Object.
  In our case, the metadata relative to EDF images are stored under the `image_edf` key, and the metadata collection itself happens in the `collect_from_edf()` function

In the `collect_from_edf()` function:

- Various components of the Dataset's name are calculated and saved.
  In these files, for corresponding images, the full Dataset name changes from one file to the other, but it contains a common suffix or identifier.
  Separating and isolating the common component of the Dataset name is therefore necessary to correctly associate the images in the two files
- Because of their relatively large size, instead of storing the full content of each image,
  a handle to the `h5py.Dataset` object is saved in the metadata.
  This will be accessed at a later stage, when calculating the change metrics.

##### Calculating comparison metrics

The change metric calculations are defined in the `ALSTomoChangeMetrics` class, inheriting from `dacman.plugins.hdf5.ObjMetadataMetrics`.

- The actual calculations take place in the `calculate()` method
  - For metadata that does not refer to EDF images, the default change metrics (from the `ObjMetadataMetrics` base class) are calculated
  - For EDF image metadata, the raw image value is accessed from the `h5py.Dataset` object collected under `dataset_obj`, and the various change metrics are computed from those
- General options of the change metrics calculations (`do_ttest`, `normalize`) are used to customize the level of detail
- For these example files, changes in Attributes for the EDF images are not interesting (as opposed to changes in File or Group Attributes).
  Therefore, the `calc_for_attributes()` method of the parent class is overridden to skip calculating change metrics for Attributes for EDF images.

##### Defining the comparator

The overall behavior of the change analysis is expressed in the `ALSTomoPlugin` comparator, inheriting from the `dacman.plugins.hdf5.HDF5Plugin` class.

- The `get_metadata_collector()` and `get_comparison_metrics()` methods tell the comparator to use our custom classes `ALSTomoMetadataCollector` and `ALSTomoChangeMetrics` to collect metadata and calculate change metrics, respectively, together with relevant options
- The `record_key_getter()` method defines which of the metadata properties should be used to create the Record index for each input file, which in turn determines which Objects will be compared in the change analysis. For this change analysis, we want to use the `image_id` metadata property, whose value is common to images in both files, for EDF images, and the `name` property for any other Object
- The `stats()` method customizes the format and amount of information returned by the change analysis

#### Running the change analysis

After making sure that the `als_tomo.py` file is in the Dac-Man plug-in directory `dacman/plugins`,
edit the `~/.dacman/config/plugins.yaml` configuration file to override the base HDF5 plug-in:

```yaml
# in ~/.dacman/config/plugins.yaml

default: DefaultPlugin
h5: ALSTomoPlugin
```

Then, run `dacman diff` on the two HDF5 files:

```sh
dacman diff als-tomo-A.h5 als-tomo-B.h5
```

---

### Changing the indexing of the comparison pairs

By default, the plug-in uses the `name` property (corresponding to the `Object.name` attribute in `h5py`) as the comparison pair index,
i.e. the key used to select corresponding Objects from each input File and associate them for the pairwise comparison.

There can be circumstances where the Object name is not unique or is not the most representative property for a particular file structure,
e.g. if Datasets have a `uid` Attribute representing a unique ID that is the same in both Files.

For these cases, it's possible to customize the creation of the Record index by passing by creating a subclass of `HDF5Plugin` and overriding the `record_key_getter` staticmethod:

```py
class UIDDatasetPlugin(HDF5Plugin):

    @staticmethod
    def record_key_getter(metadata):
        if metadata['type_h5'] == h5py.Dataset:
            return metadata['attributes']['uid']
        return metadata['name']
```

### Elementwise comparison between Attributes

Even though in the current implementation Attributes are compared as a single item, it is possible to perform a more granular comparison.
Attributes in HDF5 are mappings between text keys and values, where values can be of any supported data type.
Effectively, for the purpose of a comparison, Attributes can be considered a flat Group (i.e. no sub-groups) with one or more Datasets.
Therefore, comparisons between Attributes has similar semantics to comparison between Groups:

- Attribute keys can be present in only one of the Objects being compared; in both and values are equal; or in both and values are different
- For Attribute values, the types of change are the same as for Datasets
