import numpy as np

from dacman.core.utils import dispatch_import_error

try:
    from astropy.io import fits
except ImportError:
    dispatch_import_error(module_name='astropy', plugin_name='FITS')

try:
    import matplotlib
except ImportError:
    dispatch_import_error(module_name='matplotlib', plugin_name='FITS')

from dacman.compare import base

# TODO these are not at all CSV-specific, and at some point they should be moved to a separate common module
from dacman.plugins.csv import (
    ChangeStatus as _S,
    ChangeMetricsBase
)


class HDUImageArray(ChangeMetricsBase):
    """
    Calculate and collect change metrics for HDU containing 2D array data.
    """

    def calculate(self):
        super().calculate(exclude={'hdu_obj'})
        
        hdu_a, hdu_b = self.get_values('hdu_obj', orient=tuple)

        try:
            arr_a, arr_b = [hdu.data for hdu in (hdu_a, hdu_b)]
            arrs_eq = np.array_equal(arr_a, arr_b)
        except (ValueError, TypeError) as e:
            print(repr(e))

        if not arrs_eq:
            self.is_modified = True

            # TODO decide if/when embed the raw values in the response

            try:
                arr_delta = arr_b - arr_a
            except Exception as e:
                print(repr(e))
            else:
                # are there any meaningful aggregations/dim reductions to perform on the delta array?
                # self['delta_mean'] = 
                self.array_to_image_data(arr_a, 'a.png')
                self.array_to_image_data(arr_b, 'b.png')
                # TODO the mpl settings for this should be adapted for the fact that this is a delta,
                # with e.g. colormap centered in 0, etc
                # see e.g. https://stackoverflow.com/questions/25500541/matplotlib-bwr-colormap-always-centered-on-zero
                self.array_to_image_data(arr_delta, 'delta.png', cmap='bwr')

    def array_to_image_data(self, arr, *args, cmap='inferno', **kwargs):
        # TODO separate the plotting logic from how to store the resulting figure
        from matplotlib import pyplot as plt

        # set a non-interactive plotting backend
        # this seems to be the cause of errors encountered on macOS
        # in situations where this code was run in a thread different than main (e.g. in a Flask endpoint)
        plt.switch_backend('agg')
        # TODO decide how to pass these images to the client
        # TODO related to this: decide where to convert this data to a format accessible by the clients
        # for simplicity, we could do it here, but it would make more sense to have intermediate client-specific steps instead
        import io

        from astropy.visualization import astropy_mpl_style
        plt.style.use(astropy_mpl_style)

        plt.figure()
        plt.imshow(arr, cmap=cmap, aspect='auto')
        plt.colorbar()

        plt.savefig(*args, **kwargs)


class FITSUIPlugin(base.Comparator):
    """
    Plug-in with limited support for analyzing changes in FITS files used to try things for Dac-Man's UI.
    """

    @staticmethod
    def supports():
        return ['csv']

    @classmethod
    def description(cls):
        return cls.__doc__

    @property
    def map_name_metric(self):
        # NOTE this is an example of an interface that could be accessed by clients
        # (e.g. the UI) for information of what functionality is supported by the plug-in
        return {
            'array_difference': self.compare_as_array,
        }

    def __init__(self, metrics=None):
        
        # "metrics" is assumed to be only name + params,
        # referencing methods of this class through a dict/mapping,
        # and then use that to inform the client of the available metrics
        self.change_metrics = metrics or []

    def get_metadata_hdu(self, hdu_list, extension=0):
        md = {}

        # TODO what if the extension does not exist?
        # this is one instance of a more general issue of accessing resources
        hdu_obj = hdu_list[extension]
        # TODO also add metadata from the HDU list info/summary table
        # hdu_info = hdu_list.info(output=False)[extension]
        md['shape'] = hdu_obj.shape

        md['extension'] = extension
        md['hdu_obj'] = hdu_obj
        # we would also have the header, but for the moment we're ignoring it

        return md
    
    def compare_as_array(self, hdu_list_a, hdu_list_b, **kwargs):

        md_a = self.get_metadata_hdu(hdu_list_a, **kwargs)
        md_b = self.get_metadata_hdu(hdu_list_b, **kwargs)

        key = None

        metric = HDUImageArray(key, md_a, md_b)
        metric.calculate()
        return dict(metric)

    def compare(self, path_a, path_b):

        total_res = {}

        hdu_list_a = fits.open(path_a)
        hdu_list_b = fits.open(path_b)

        for chm_info in self.change_metrics:
            # TODO handle errors (and possibly factor out to single-item method)
            name = chm_info['name']
            params = chm_info['params']
            func = self.map_name_metric[name]
            res = func(hdu_list_a, hdu_list_b, **params)
            total_res[name] = res

        hdu_list_a.close()
        hdu_list_b.close()

        return total_res

    def percent_change(self):
        return np.nan

    def stats(self):
        return {}

