# Analyzing changes in multi-format HDF5 files

The capability of HDF5 files of storing arbitrary data within a complex structure means that the range of possible comparisons is effectively unlimited.
Rather than trying to anticipate all possible use cases, the plug-in is designed so that it is possible for users to modify the default behavior, and extend it with more specialized functionality.

This example illustrates how to extend the included HDF5 plug-in to analyze changes
in a set of EDF image files stored inside a complex HDF5 file,
customizing the HDF5 functionality to match the structure of the source data
and adding custom change metric calculations.

!!! tip
    The complete code for this example can be found in [`examples/hdf5_edf/edf_change_ana.py`](https://github.com/deduce-dev/dac-man/blob/master/examples/hdf5_edf/edf_change_ana.py).

## Overview

These are the steps needed to implement the custom functionality.
For reference, the general phases of the data processing performed by the HDF5 plug-in are described [here](../../../plugins/hdf5/).

- Adapting the collection of metadata from the Objects in the source files, including how to identify the EDF image files that the change analysis focuses on
- Adapting the criteria for comparison to the source files structure, i.e. specifying which Objects from each source file should be compared
- Integrating the custom change metric calculation within the HDF5 plug-in processing pipeline
- Customizing the output format

## Collecting metadata

The first step is to define how metadata will be collected from each Object in each input File.
For this, we create `ALSTomoMetadataCollector`, a subclass of `dacman.plugins.hdf5.metadata.MetadataCollector`.

```py
from dacman.plugins import hdf5 as dacman_h5


class ALSTomoMetadataCollector(dacman_h5.metadata.ObjMetadataCollector):
    pass
```

The custom behavior is grouped in two methods:

The `is_edf_dataset` property is used to define which Datasets should be treated as EDF images.
In this example, the name of the Dataset is used as the basis for this criteria,
but other properties could be used as well, to e.g. select Datasets based on their shape or data type.

```py
class ALSTomoMetadataCollector(dacman_h5.metadata.ObjMetadataCollector):

    @property
    def is_edf_dataset(self):
        return self.is_dataset and self.obj.name.endswith('.edf')
```

The `collect()` method defines how the metadata is collected depending on the characteristics of the Object.
In our case, the metadata relative to EDF images are stored under the `image_edf` key, and the metadata collection itself happens in the `collect_from_edf()` function

```py
class ALSTomoMetadataCollector(dacman_h5.metadata.ObjMetadataCollector):

    @property
    def is_edf_dataset(self):
        return self.is_dataset and self.obj.name.endswith('.edf')

    def collect(self):

        if self.is_edf_dataset:
            dacman_h5.metadata.collect_from_obj(self, name=self.name, obj=self.obj)

            self['image_edf'] = {}
            collect_from_edf(self['image_edf'], self.obj)
        else:
            super().collect()
```

The actual collection of metadata takes place in the `collect_from_edf()` function.

First, various components of the Dataset's name are calculated and saved.
In these files, for corresponding images, the full Dataset name changes from one file to the other,
but it contains a substring representing `image_idx`, an identifier that's common to both files.
Extracting the common identifier from the Dataset name is therefore necessary to correctly associate the images
in the two source files for comparison.

```py
def collect_from_edf(md, dataset):
    # using pathlib.Path (treating Object.name as an absolute filesystem path) for convenience
    ds_name_as_path = Path(dataset.name)
    ds_basename = ds_name_as_path.name
    # stem = last component of basename without extension
    ds_stem = ds_name_as_path.stem

    md['image_basename'] = ds_basename
    md['image_stem'] = ds_stem
    md['image_id'] = ds_stem.split('__')[-1]
    md['image_idx'] = int(md['image_id'].split('_')[-1])
```

To limit memory usage, because of the large size, we don't save the entire array contained in the Dataset with the rest of the metadata.
Instead, we store a handle to the `h5py.Dataset` object,
that will be accessed at a later stage when calculating the change metrics.

```py
def collect_from_edf(md, dataset):
    # using pathlib.Path (treating Object.name as an absolute filesystem path) for convenience
    ds_name_as_path = Path(dataset.name)
    ds_basename = ds_name_as_path.name
    # stem = last component of basename without extension
    ds_stem = ds_name_as_path.stem

    md['image_basename'] = ds_basename
    md['image_stem'] = ds_stem
    md['image_id'] = ds_stem.split('__')[-1]
    md['image_idx'] = int(md['image_id'].split('_')[-1])

    md['dataset_obj'] = dataset
```

## Calculating custom change metrics

The custom change metrics we want to calculate can be represented by this Python function:

```py
import scipy.stats
import sklearn.metrics


def two_frame_change_analysis(arr_2d_A, arr_2d_A, do_ttest=False):

    rms = sqrt(mean_squared_error(arr_2d_A, arr_2d_B)) #compute RMSE between the 2 input frames

    min_d = min(min(arr_2d_A), min(arr_2d_B))
    max_d = max(max(arr_2d_A), max(arr_2d_B))

    rms_log = np.log(rms) #logarithm of RMSE

    if do_ttest:
        t_test_t, t_test_p = stats.ttest_ind(arr_2d_A, arr_2d_B, equal_var=True)
    else:
        t_test_t = None
        t_test_p = None

    change_data = {
      'min_d': min_d,
      'max_d': max_d,
      'rms_log': rms_log,
      't_test_t': t_test_t,
      't_test_p': t_test_p,
    }

    return change_data
```

To integrate these calculations with the HDF5 plug-in,
we start by creating the `ALSTomoChangeMetrics` class,
inheriting from `dacman.plugins.hdf5.ObjMetadataMetrics`:

```py
class ALSTomoChangeMetrics(dacman_h5.ObjMetadataMetrics):
    pass
```

Its `calculate()` method implements the actual calculations.
For metadata that does not belong to EDF images,
only the default change metrics are calculated, using the parent class `ObjMetadataMetrics`:

```py
class ALSTomoChangeMetrics(dacman_h5.ObjMetadataMetrics):

    @property
    def is_image_edf(self):
        return 'image_edf' in self.properties

    def calculate(self):
        super().calculate()
```

For EDF image metadata, the custom change metrics are calculated.
The raw image data, a 2D array, is accessed from the `h5py.Dataset` object collected under the `dataset_obj` property,
and the various change metrics are computed from the values extracted from the two objects being compared.
The boolean `do_ttest` is supplied as an optional argument when creating the `ALSTomoChangeMetrics` object.

```py
class ALSTomoChangeMetrics(dacman_h5.ObjMetadataMetrics):

    def __init__(self, *args, do_ttest=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_ttest = do_ttest

    @property
    def is_image_edf(self):
        return 'image_edf' in self.properties

    def calculate(self):
        super().calculate()

        if self.is_image_edf:
            if self.change_in('image_edf'):
                self.is_modified = True
                md_a, md_b = self.get_values('image_edf', orient=tuple)

                dset_a, dset_b = [md['dataset_obj'] for md in (md_a, md_b)]

                matrix_a, matrix_b = [dset[0,:,:] for dset in (dset_a, dset_b)]

                min_a, min_b = [numpy.amin(arr) for arr in (matrix_a, matrix_b)]
                max_a, max_b = [numpy.amax(arr) for arr in (matrix_a, matrix_b)]

                # we use the normal Python max/min because these two values are already scalars
                self['min_d'] = min([min_a, min_b])
                self['max_d'] = max([max_a, max_b])

                self['rms'] = numpy.sqrt(sklearn.metrics.mean_squared_error(matrix_a, matrix_b))

                # this depends on whether we want nans/infinities in the final result or not
                LOG_EPSILON = 10e-6
                self['rms_log'] = numpy.log(self['rms'] + LOG_EPSILON)

                flat_a, flat_b = [numpy.ravel(mat) for mat in (matrix_a, matrix_b)]

                if self.do_ttest:
                    ttest_t, ttest_p = scipy.stats.ttest_ind(flat_a, flat_b, equal_var=True)

                    self['ttest_t'] = ttest_t
                    self['ttest_p'] = ttest_p
```

## Creating the custom comparator class

The last custom class that we have to implement is `ALSTomoPlugin`,
an extension of the `HDF5Plugin` comparator class.
The role of this class is to couple all of our custom object
and manage how the overall change analysis options.

```py
from dacman.plugins import hdf5 as dacman_h5


class ALSTomoPlugin(dacman_h5.HDF5Plugin):
    pass
```

First, we integrate our custom classes for metadata collection and change metrics calculation,
exposing their options as class attributes,
by overriding the `get_metadata_collector()` and `get_comparison_metrics()` methods:

```py
class ALSTomoPlugin(dacman_h5.HDF5Plugin):

    options = {
        'do_ttest': True,
    }

    def get_metadata_collector(self, *args, **kwargs):
        return super().get_metadata_collector(*args, obj_collector_cls=ALSTomoMetadataCollector, **kwargs)

    def get_comparison_metrics(self, *args, **kwargs):
        return ALSTomoChangeMetrics(*args, **self.options, **kwargs)
```

The `record_key_getter()` method defines which of the metadata properties should be used to create the Record index for each input file,
which in turn determines which Objects will be compared in the change analysis.
For this change analysis, we want to use the `image_id` metadata property,
whose value is common to images in both files, for EDF images,
and the `name` property for all other Objects.

```py
class ALSTomoPlugin(dacman_h5.HDF5Plugin):

    options = {
        'do_ttest': True,
    }

    def get_metadata_collector(self, *args, **kwargs):
        return super().get_metadata_collector(*args, obj_collector_cls=ALSTomoMetadataCollector, **kwargs)

    def get_comparison_metrics(self, *args, **kwargs):
        return ALSTomoChangeMetrics(*args, **self.options, **kwargs)

    @staticmethod
    def record_key_getter(metadata):

        if 'image_edf' in metadata:
            return metadata['image_edf']['image_id']
        return metadata['name']
```

## Creating the custom analysis script

We start from adding a `main()` function wrapping our custom comparator class
and performing the change analysis:

```py
def main():
    import sys

    plugin = ALSTomoPlugin()
    print(plugin.description())

    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    path_a, path_b = cli_args[0], cli_args[1]

    plugin.compare(path_a, path_b)


if __name__ == "__main__":
    main()
```

### Customizing the level of detail of the output

As a way to customize the amount of information returned when the analysis is complete,
we add a way to select the level of detail in the output.
By default, only the change percentage will be displayed;
If `DETAIL_LEVEL` is set to 2 or greater, the full change metrics information will be printed as JSON.

```py
DETAIL_LEVEL = 1

def main():
from dacman.plugins.hdf5.util import to_json

    import sys

    plugin = ALSTomoPlugin()
    print(plugin.description())

    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    path_a, path_b = cli_args[0], cli_args[1]

    plugin.compare(path_a, path_b)

    if DETAIL_LEVEL >= 1:
        print(f'Percent change: {plugin.percent_change():.2f}%')
    if DETAIL_LEVEL >= 2:
        print(to_json(plugin._metrics))


if __name__ == "__main__":
    main()
```

## Installing additional dependencies

On top of the default Dac-Man dependencies and the `h5py` package required by the [HDF5 plug-in](../../../plugins/hdf5), the custom change metrics in this change analysis uses functions from the `scipy` and `scikit-learn` libraries.
To install the corresponding packages, from the environment where Dac-Man is installed, run:

```sh
# install packages using Conda
conda install scipy scikit-learn

# or, alternatively, using pip
python -m pip install scipy scikit-learn
```

## Running the change analysis

After adding the `#!/usr/bin/env python3` line at the top of the file and setting the file as executable,
run the change analysis on the two example files given in `examples/hdf5_edf`:

```sh
dacman diff als-tomo-A.h5 als-tomo-B.h5 --script edf_change_ana.py
```
