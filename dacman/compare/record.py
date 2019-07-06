
import os
import re

# file-format specific import checks to ensure the package is installed
# for FITS
try:
    from astropy.io import fits
    ASTROPY_IMPORT = True
except ImportError:
    ASTROPY_IMPORT = False
# for edf
try:
    import fabio
    FABIO_IMPORT = True
except ImportError:
    FABIO_IMPORT = False
# for HDF5
try:
    import h5py
    H5_IMPORT = True
except ImportError:
    H5_IMPORT = False
import sys
try:
    import numpy
except ImportError:
    if ASTROPY_IMPORT == True or H5_IMPORT == True:
        print('numpy not installed, but required!')
        sys.exit()

from dacman.compare.base import DacmanRecordAdaptor


##########################################################

class DefaultAdaptor(DacmanRecordAdaptor):
    def __init__(self):
        pass

    def transform(self, data_file):
        header_records = []
        data_records = []
        with open(data_file) as f:
            for line in f:
                words = re.findall(r"[\w']+", line)
                data_records += words

        return header_records, data_records


class H5Adaptor(DacmanRecordAdaptor):
    def __init__(self):
        pass

    def transform(self, hdf_file):
        pass


class FitsAdaptor(DacmanRecordAdaptor):
    def __init__(self):
        pass

    def transform(self, fits_file):
        hdulist = fits.open(fits_file)
        hdu_header_records = []
        hdu_data_records = []
        for i in range(len(hdulist)):
            hdu = hdulist[i]
            header_record, data_record = self.__hdu2records__(hdu)
            hdu_header_records.append(header_record)
            hdu_data_records.append(data_record)
        return hdu_header_records, hdu_data_records

    def __hdu2records__(self, hdu):
        header_record_list = []
        data_record_list = []
        for k, v in hdu.header.items():
            header_record_list.append('{}: {}'.format(k, v))

        data_dims = self.__get_hdu_shape__(hdu)
        if len(data_dims) == 2: # 2-D array
            for row in hdu.data:
                data_record_list.append(row.tolist())
        else: # n-D array
            for row in hdu.data:
                flat_data = self.__flatten_ndarray__(row)
                data_record_list.append(flat_data.tolist())

        return header_record_list, data_record_list

    def __get_hdu_shape__(self, hdu):
        dims = hdu._summary()[4]
        if not isinstance(hdu, fits.hdu.table.TableHDU):
            return hdu.data.shape
        else:
            row_col = dims.replace('R', '').replace('C', '').split(' x ')
            dims = (int(row_col[0]), int(row_col[1]))
            return dims


class ImageAdaptor(DacmanRecordAdaptor):
    def __init__(self):
        pass

    def transform(self, image_file):
        img = fabio.open(image_file)
        header_record_list = []
        data_record_list = []
        for k, v in img.header.items():
            header_record_list.append('{}: {}'.format(k, v))

        data_dims = img.data.shape
        if len(data_dims) == 2:  # 2-D array
            for row in img.data:
                data_record_list.append(row.tolist())
        else:  # n-D array
            for row in img.data:
                flat_data = self.__flatten_ndarray__(row)
                data_record_list.append(flat_data.tolist())

        return header_record_list, data_record_list


###################################################################

class DacmanRecord(object):
    def __init__(self, source):
        self.source = source
        self.headers = None
        self.data = None
        self.metadata = None
        self.file_support = {}
        self.file_adaptors = {}
        self.__import_file_support__()
        self.__transform_source__()

    def get_header(self):
        return self.headers

    def get_data(self):
        return self.data

    def get_metadata(self):
        return self.metadata

    def __transform_source__(self):
        adaptor = self.__filetype__(self.source)
        if adaptor is None:
            adaptor = DefaultAdaptor()
        headers, data = adaptor.transform(self.source)
        self.headers = headers
        self.data = data
        self.metadata = {'nHeaders': len(headers), 'nValues': len(data)}

    def __import_file_support__(self):
        hdf_exts = ['.hdf', '.h4', '.hdf4', '.he2', '.h5', '.hdf5', '.he5']
        for hdf_ext in hdf_exts:
            self.file_support[hdf_ext] = H5_IMPORT
            self.file_adaptors[hdf_ext] = H5Adaptor

        self.file_support['edf'] = FABIO_IMPORT
        self.file_adaptors['edf'] = ImageAdaptor

        self.file_support['tif'] = FABIO_IMPORT
        self.file_adaptors['tif'] = ImageAdaptor

        self.file_support['fits'] = ASTROPY_IMPORT
        self.file_adaptors['fits'] = FitsAdaptor

    '''
    temporary solution to get file types using extensions
    later use magic to get the file header to determine file type
    '''
    def __filetype__(self, filename):
        file_ext = os.path.splitext(filename)[1][1:].lower()
        if file_ext in self.file_support:
            if self.file_support[file_ext]:
                adaptor = self.file_adaptors[file_ext]()
                return adaptor
            else:
                return None
        else:
            return None



