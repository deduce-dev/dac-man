# Capturing Changes in Multi-Format Files (HDF5 + EDF): An ALS Use Case

A common use case for using plug-ins would be to add a comparison for a specialized type of Dataset.
The additional functionality can be added by minimally extending the main classes involved in the change analysis chain.

As an example case study, we consider analyzing changes in images stored in HDF5 files in the EDF format.
The complete code for this example can be found in [`examples/hdf5_edf/edf_change_ana.py`](https://github.com/dghoshal-lbl/dac-man/blob/master/examples/hdf5_edf/edf_change_ana.py).

## Installing extra dependencies

On top of the default Dac-Man dependencies and the `h5py` package required by the [HDF5 plug-in](../../plugins/hdf5), custom change analyses might require additional dependencies.

The `edf_change_ana` change analysis uses functions from the `numpy`, `scipy`, and `scikit-learn` Python modules.
To install them, from the environment where Dac-Man is installed, run:

```sh
# install packages using Conda
conda install numpy scipy scikit-learn

# or, alternatively, using pip
python -m pip install numpy scipy scikit-learn
```

## Developing the extension

A brief walkthrough of the code for `edf_change_ana.py` is presented below.

### Collecting metadata

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

### Calculating comparison metrics

The change metric calculations are defined in the `ALSTomoChangeMetrics` class, inheriting from `dacman.plugins.hdf5.ObjMetadataMetrics`.

- The actual calculations take place in the `calculate()` method
  - For metadata that does not refer to EDF images, the default change metrics (from the `ObjMetadataMetrics` base class) are calculated
  - For EDF image metadata, the raw image value is accessed from the `h5py.Dataset` object collected under `dataset_obj`, and the various change metrics are computed from those
- General options of the change metrics calculations (`do_ttest`, `normalize`) are used to customize the level of detail
- For these example files, changes in Attributes for the EDF images are not interesting (as opposed to changes in File or Group Attributes).
  Therefore, the `calc_for_attributes()` method of the parent class is overridden to skip calculating change metrics for Attributes for EDF images.

### Defining the comparator

The overall behavior of the change analysis is expressed in the `ALSTomoPlugin` comparator, inheriting from the `dacman.plugins.hdf5.HDF5Plugin` class.

- The `get_metadata_collector()` and `get_comparison_metrics()` methods tell the comparator to use our custom classes `ALSTomoMetadataCollector` and `ALSTomoChangeMetrics` to collect metadata and calculate change metrics, respectively, together with relevant options
- The `record_key_getter()` method defines which of the metadata properties should be used to create the Record index for each input file, which in turn determines which Objects will be compared in the change analysis. For this change analysis, we want to use the `image_id` metadata property, whose value is common to images in both files, for EDF images, and the `name` property for any other Object
- The `stats()` method customizes the format and amount of information returned by the change analysis

## Running the change analysis

After making sure that the `edf_change_ana.py` file is executable,
run `dacman diff` on the two HDF5 files specifying the script's path with the `--script` option:

```sh
dacman diff als-tomo-A.h5 als-tomo-B.h5 --script edf_change_ana.py
```
