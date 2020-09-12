#!/usr/bin/env python3
"""
An example extension/customization of the Dac-Man HDF5 plugin for a specialized use case.

The datasets to compare are modeled after tomography frames from an ALS beamline, saved in HDF5 file as .edf datasets.
The filenames of the original reference files are:

  - A: 20140905_191647_YL1031_.h5
  - B: 20160903_221332_FACS_140deg2_.h5

Extra dependencies:

- scipy
  - scipy.stats.ttest_ind()
- sklearn
  - sklearn.metrics.mean_squared_error()
"""


from pathlib import Path

import numpy
import scipy.stats
import sklearn.metrics

from dacman.plugins import hdf5 as dacman_h5
from dacman.plugins.hdf5.util import to_json


# adapted version from Abdelrahman's code in `dacman_stream`
# this is just here for ease of reference: it's not runnable as-is
def two_frame_analysis(dataA, dataB):
    rms_log = None
    t_test_t = None
    t_test_p = None
    do_ttest = True

    matrix1 = dataA
    matrix2 = dataB

    #matrix1 = dataA.flatten()
    #matrix2 = dataB.flatten()

    rms = sqrt(mean_squared_error(matrix1, matrix2)) #compute RMSE between the 2 input frames
    min_d = min(min(matrix1), min(matrix2))
    max_d = max(max(matrix1), max(matrix2))
    
    rms_log = np.log(rms) #logarithm of RMSE

    if do_ttest:
        #option 1: t-test over the whole frame
        t_test_t, t_test_p = stats.ttest_ind(matrix1, matrix2, equal_var=True)
    
    return rms_log, t_test_t, t_test_p


def collect_from_edf(md, dataset):
    # using pathlib.Path (treating Object.name as an absolute filesystem path) for convenience
    ds_name_as_path = Path(dataset.name)
    ds_basename = ds_name_as_path.name
    # stem = last component of basename without extension
    ds_stem = ds_name_as_path.stem

    # maybe all of this would be easier using the "parse" module
    # (the "proper" way to do this would be to define a grammar)
    # 20160903_221332_FACS_140deg2_/2M/FACS_140deg2__2m_00299.edf
    # {date}_{time}_{measurement_id}/2M/{measurement_id}_{dataset_id}.edf
    # if this fails, skip

    md['image_basename'] = ds_basename
    md['image_stem'] = ds_stem
    # here I think that the separator is not actually a double underscore,
    # but there's a trailing underscore in the measurement_id
    md['image_id'] = ds_stem.split('__')[-1]
    try:
        md['image_idx'] = int(md['image_id'].split('_')[-1])
    except ValueError:
        # in our specific case, this happens because there are a few .edf Datasets that don't follow the same naming scheme
        md['image_idx'] = None

    # to actually get the matrix from the full array, we slice the array to exclude the first dimension
    # arr = dataset[...]
    # matrix = arr[0,:10,:10]
    # probably we could do this in one step directly from the dataset
    # not only we could, but we should
    # arr = dataset[...] reads in the whole array
    # matrix = arr[0, :10, :10] returns a view of arr
    # since matrix is saved in the metadata dictionary, this means that
    # a reference to the arr object is persisted, and so it doesn't get garbage collected
    # reading the matrix directly should side-step this problem

    # instead of the whole array, we can keep a reference to the dataset object
    # and then read it on demand within the comparison function
    # in this case, we have to be careful to close the file after the comparison
    # (as opposed to after creating the record)
    md['dataset_obj'] = dataset


class ALSTomoMetadataCollector(dacman_h5.metadata.ObjMetadataCollector):

    @property
    def is_edf_dataset(self):
        # TODO possibly add constraint about dataset shape?
        return self.is_dataset and self.obj.name.endswith('.edf')

    def collect(self):

        if self.is_edf_dataset:
            # TODO make these more modular, e.g. it would be more convenient to have self.collect_from_obj()
            dacman_h5.metadata.collect_from_obj(self, name=self.name, obj=self.obj)

            self['image_edf'] = {}
            collect_from_edf(self['image_edf'], self.obj)
        else:
            super().collect()


class ALSTomoChangeMetrics(dacman_h5.ObjMetadataMetrics):

    def __init__(self, *args, do_ttest=True, normalize=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_ttest = do_ttest
        self.normalize = normalize

    @property
    def is_image_edf(self):
        return 'image_edf' in self.properties

    def calculate(self):
        # like in the metadata collector, this is also optional
        # TODO check how calculate() behaves when properties are missing (because they were not collected)
        # it should not crash, but maybe it's better to issue a warning
        # WARNING: properties [foo, bar] are required by the change metric calculation, but could not be found
        # this is not very optional, since it also assigns the status
        # maybe the status should be assigned as a separate method
        # (which would also allow to customize if the status should be assigned
        # before or after calculating the metrics)
        self['key'] = self.key
        super().calculate()

        if self.is_image_edf:
            # this is true if any of the metadata values are different
            # since we're passing a h5.Dataset object, this will always be true
            # so we might want to assign the status later and/or skip the self.change_in() entirely
            # also, the name "change_in" is arguably a bit misaligned with the idea that "change" represents a high-level,
            # more general concept
            # since we're using this to trigger further comparisons, we could refer to "equal",
            # e.g. "values_not_equal(prop)"
            if self.change_in('image_edf'):
                self.is_modified = True
                md_a, md_b = self.get_values('image_edf', orient=tuple)

                # matrix_a, matrix_b = [props['matrix'] for props in (props_a, props_b)]
                # instead of saving the array in the metadata, save a reference to the h5.Dataset object instead
                # and extract the data only here, where it will be used
                # matrix_a, matrix_b = [props['dataset_obj'][0, :, :] for props in (props_a, props_b)]
                dset_a, dset_b = [md['dataset_obj'] for md in (md_a, md_b)]

                matrix_a, matrix_b = [dset[0,:,:] for dset in (dset_a, dset_b)]

                min_a, min_b = [numpy.amin(arr) for arr in (matrix_a, matrix_b)]
                max_a, max_b = [numpy.amax(arr) for arr in (matrix_a, matrix_b)]

                self['maxmin_a'] = max_a - min_a
                self['maxmin_b'] = max_b - min_b

                # we use the normal Python max/min because these two values are already scalars
                self['min_d'] = min([min_a, min_b])
                self['max_d'] = max([max_a, max_b])

                def normalize(arr):
                    zero_based = arr - arr.min()
                    return zero_based / zero_based.max()
                
                if self.normalize:
                    matrix_a, matrix_b = [normalize(mat) for mat in (matrix_a, matrix_b)]

                self['rms'] = numpy.sqrt(sklearn.metrics.mean_squared_error(matrix_a, matrix_b))

                # this depends on whether we want nans/infinities in the final result or not
                LOG_EPSILON = 10e-6
                self['rms_log'] = numpy.log(self['rms'] + LOG_EPSILON)

                flat_a, flat_b = [numpy.ravel(mat) for mat in (matrix_a, matrix_b)]

                if self.do_ttest:
                    ttest_t, ttest_p = scipy.stats.ttest_ind(flat_a, flat_b, equal_var=True)

                    self['ttest_t'] = ttest_t
                    self['ttest_p'] = ttest_p

    def calc_for_attributes(self):
        """
        Skip calculating changes in attributes for EDF images
        """
        if self.is_image_edf:
            return
        super().calc_for_attributes()


class ALSTomoPlugin(dacman_h5.HDF5Plugin):
    
    @staticmethod
    def description():
        # return module-level docstring
        return globals()['__doc__']

    options = {
        'do_ttest': True,
        'normalize': False
    }

    @staticmethod
    def supports():
        return ['h5']

    def get_metadata_collector(self, *args, **kwargs):
        return super().get_metadata_collector(*args, obj_collector_cls=ALSTomoMetadataCollector, **kwargs)

    # TODO change "comparison metrics" to "change metrics"?
    def get_comparison_metrics(self, *args, **kwargs):
        return ALSTomoChangeMetrics(*args, **self.options, **kwargs)

    @staticmethod
    def record_key_getter(metadata):
        """
        Return index key to associate Objects from each input.

        For EDF Datasets, since the group names (and thus the `name` property) are different,
        we use `image_id` (which is the same across the two files) to identify the image
        """

        if 'image_edf' in metadata:
            return metadata['image_edf']['image_id']
        return metadata['name']

    def stats(self, changes):
        """
        Override the normal method, since stats from HDF5Plugin are not very relevant for this use case.
        """

        print(to_json(changes))


# copy-pasted from dacman_h5.__main__ for debugging outside of `dacman diff`
def main():
    import sys
    import argparse
    from pathlib import Path

    plugin = ALSTomoPlugin()
    print(plugin.description())

    parser = argparse.ArgumentParser(description=plugin.description())
    parser.add_argument('path_a', metavar='A', type=Path, help='Path to first HDF5 file to compare.')
    parser.add_argument('path_b', metavar='B', type=Path, help='Path to second HDF5 file to compare.')

    args = parser.parse_args()
    DETAIL_LEVEL = 1

    plugin.compare(args.path_a, args.path_b, obj_name=None)

    if DETAIL_LEVEL >= 0:
        print(f'Percent change: {plugin.percent_change():.2f}%')
    if DETAIL_LEVEL >= 1:
        plugin.stats(plugin._metrics)
    if DETAIL_LEVEL >= 2:
        print(to_json(plugin._metrics))


if __name__ == "__main__":
    main()
