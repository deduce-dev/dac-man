"""
`dacman.core.analyzer`
====================================

.. currentmodule:: dacman.core.analyzer

:platform: Unix, Mac
:synopsis: Module implementing different `data adaptors` to transform data into Dac-Man records

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

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

import hashlib
from itertools import islice
import os
import sys
import difflib

from dacman.core.change import Change
import dacman.core.utils as dacman_utils
from dacman.core.utils import cprint

__modulename__ = 'analyzer'

'''
Algorithm to compute differences in data
-----------------------------------------
Generalization: Each data file contains records.
                A 'record' can be line of text, an array of integers, or an n-dimensional
                entity that identifies a single measurement data.
                Each record consists of 'words', where a word is a single immutable entity
                of a measurement. Examples are a word in a sentence, an integer in an array etc.
Assumption: This module should be used only when it has been established that the files in
            question have been modified, and are different versions of the same file.
Algorithm:
         1. Transform a data file into a list of records
         2. For an n-dimensional measurement data, map it to a 1-dimensional record of words
         3. To find the diff, compare the words in the list of records (from the data files)
         4. Use Myer's diff algorithm (using LCS) to find the diff between two list of records
         5. For any two lists l1 and l2:
            a) A record, r is said to be 'added' in l1, 
               if r is present in l1 and if no common subsequence of r is present in l2
            b) A record, r is said to be 'deleted' from l1,
               if r is present in l2 and if no common subsequence of r is present in l1
            c) A record, r is said to be 'modified' in l1 and l2,
               if a common subsequence of r in l1 is present in l2
'''


'''
class that calculates changes based on the file/data types
'''
class Analyzer():
    def __init__(self):
        self.comparer_map = {'unknown': self.default_analyzer,
                             'hdf': self.hdf_analyzer,
                             'h5': self.hdf_analyzer,
                             'edf': self.image_analyzer,
                             'tif': self.image_analyzer,
                             'fits': self.fits_analyzer}


        self.lib_support = {'unknown': True,
                            'hdf': H5_IMPORT,
                            'h5': H5_IMPORT,
                            'edf': FABIO_IMPORT,
                            'tif': FABIO_IMPORT,
                            'fits': ASTROPY_IMPORT}

        #self.graphgen = plotter.GraphGen()


    '''
    temporary solution to get file types using extensions
    later use magic to get the file header to determine file type
    '''
    def __filetype__(self, filename):
        file_ext = os.path.splitext(filename)[1][1:].lower()
        if file_ext in self.comparer_map:
            return file_ext
        else:
            return 'unknown'
        

    def __get_comparison_id__(self, file1, file2):
        hash_string = '{}{}deduce'.format(file1, file2)
        #outdir = os.path.join(os.getcwd(), hashlib.md5(hash_string.encode('utf-8')).hexdigest())
        #return outdir
        id = hashlib.md5(hash_string.encode('utf-8')).hexdigest()
        return id

    '''
    the interface to auto-select the change analyzer based on file types
    '''
    def analyze(self, file1, file2):
        filetype1 = self.__filetype__(file1)
        filetype2 = self.__filetype__(file2)
        if filetype1 == filetype2:
            if self.lib_support[filetype1]:
                change_analyzer = self.comparer_map[filetype1]
                change_analyzer(file1, file2)
            else:
                self.default_analyzer(file1, file2)            
        else:
            self.__type__ = 'unknown'
            self.default_analyzer(file1, file2)


    '''
    the default interface to analyze changes
    - considers a data file to be a list of strings
    - a record is a single line in the data file
    '''
    def default_analyzer(self, file1, file2):
        cprint(__modulename__, 'Using default Deduce analyzer')
        cprint(__modulename__, 'Normalizing data into Deduce records')
        record_list1 = []
        record_list2 = []
        with open(file1) as f:
            record_list1 = f.readlines()            
        with open(file2) as f:
            record_list2 = f.readlines()

        diff_metadata = {}

        #outdir = os.path.join(os.getcwd(), hashlib.md5(file1+file2+'deduce').hexdigest())
        '''
        outdir = self.__get_outdir__(file1, file2)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        '''
        compare_id = dacman_utils.hash_comparison_id(file1, file2)

        cprint(__modulename__, 'Comparing Deduce records')
        data_change, data_edits = self.compare(record_list1, record_list2)

        self.display('Data', data_edits)

        data_metadata = {}
        cprint(__modulename__, 'Saving metadata describing data change')
        self.__set_change_metadata__(data_metadata, data_change)
        metadata = {'data': data_metadata}
        outfile = self.save(compare_id, file1, file2, metadata)
        cprint(__modulename__, 'Change analysis saved in {}'.format(outfile))


    '''
    HDF-specific change analyer
    - considers a data file to be a list of datasets
    - a record is a single dataset in the file
    '''
    def hdf_analyzer(self, file1, file2):
        cprint(__modulename__, 'HDF analyzer not yet implemented!')
        

    '''
    Change analyzer specific to 2D detector data: EDF, TIFF
    - assumes image data for EDF, TIFF types that can be processed by the fabio module
    - a record is either header or data
    '''
    def image_analyzer(self, file1, file2):
        cprint(__modulename__, 'Using change analyzer for 2D detector data')
        cprint(__modulename__, 'Normalizing data into Deduce records')
        header_record1, data_record1 = self.__transform_image__(file1)
        header_record2, data_record2 = self.__transform_image__(file2)
        header_lines = []
        data_lines = []

        #outdir = os.path.join(os.getcwd(), hashlib.md5(file1+file2+'deduce').hexdigest())
        '''
        outdir = self.__get_outdir__(file1, file2)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        '''
        compare_id = dacman_utils.hash_comparison_id(file1, file2)

        cprint(__modulename__, 'Comparing Deduce records')
        header_change, header_edits = self.compare(header_record1, header_record2)
        #print('Change summary in image headers')
        #self.display(header_change, verbose=True)
        nrecs1 = len(data_record1)
        nrecs2 = len(data_record2)
        data_edits = []
        record_changes = []
        if nrecs1 == nrecs2:
            for i in range(nrecs1):
                record_change, record_edits = self.compare(data_record1[i], data_record2[i])
                data_edits[len(data_edits):] = record_edits[:]
                record_changes.append(record_change)
        else:
            if nrecs1 < nrecs2: # if more new records are added
                pass 
            else: # if more old records are deleted
                pass
        
        cprint(__modulename__, 'Summarizing record changes')
        data_change = self.summarize_change(record_changes)

        self.display('Data', data_edits)
        self.display('Header', header_edits)

        cprint(__modulename__, 'Saving metadata describing data change')
        header_metadata = {}
        data_metadata = {}
        self.__set_change_metadata__(header_metadata, header_change)
        self.__set_change_metadata__(data_metadata, data_change)
        metadata = {'headers': header_metadata, 'data': data_metadata}
        outfile = self.save(compare_id, file1, file2, metadata)
        cprint(__modulename__, 'Change analysis saved in {}'.format(outfile))
        #print('Change summary in image data')
        #self.display(data_change)


    def summarize_change(self, change_list): 
        added = []
        deleted = []
        modified = []
        unchanged = []
        for record_change in change_list:
            added[len(added):] = record_change.added[:]
            deleted[len(deleted):] = record_change.deleted[:]
            modified[len(modified):] = record_change.modified[:]
            unchanged[len(unchanged):] = record_change.unchanged[:]               
        change = Change(added, deleted, modified, unchanged)
        change.calculate_degree()
        return change


    '''
    FITS-specific change analyzer
    - each hdulist header and data is a record
    '''
    def fits_analyzer(self, file1, file2):
        cprint(__modulename__, 'Using FITS change analyzer')
        hdulist1 = fits.open(file1)
        hdulist2 = fits.open(file2)
        header_lines = []
        data_lines = []

        #outdir = os.path.join(os.getcwd(), hashlib.md5(file1+file2+'deduce').hexdigest())
        '''
        outdir = self.__get_outdir__(file1, file2)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        '''
        compare_id = dacman_utils.hash_comparison_id(file1, file2)

        if len(hdulist1) == len(hdulist2):
            header_metadata = {}
            data_metadata = {}
            for i in range(len(hdulist1)):
            #for i in range(2,3):
                has_header_changed = False
                has_data_changed = False
                hdu1 = hdulist1[i]
                hdu2 = hdulist2[i]
                cprint(__modulename__, 'Calculating changes in HDU={}'.format(hdu1.name))
                cprint(__modulename__, 'Normalizing HDU data into Deduce records')
                header_record1, data_record1 = self.__transform_hdu__(hdu1)
                header_record2, data_record2 = self.__transform_hdu__(hdu2)

                header_change, header_edits = self.compare(header_record1, header_record2)
                nrecs1 = len(data_record1)
                nrecs2 = len(data_record2)
                data_edits = []
                record_changes = []
                if nrecs1 == nrecs2:
                    #print("**** HDU - {}".format(hdu1.name))
                    for i in range(nrecs1):
                        #print("Record-{}".format(i))
                        record_change, record_edits = self.compare(data_record1[i], data_record2[i])
                        data_edits[len(data_edits):] = record_edits[:]
                        record_changes.append(record_change)
                else:
                    if nrecs1 < nrecs2: # if more new records are added
                        pass 
                    else: # if more old records are deleted
                        pass
                
                cprint(__modulename__, 'Summarizing record changes')
                data_change = self.summarize_change(record_changes)

                self.display('{}.Headers'.format(hdu1.name), header_edits)
                self.display(hdu1.name, data_edits)

                header_metadata[hdu1.name]= {}
                data_metadata[hdu1.name] = {}
                self.__set_change_metadata__(header_metadata[hdu1.name], header_change)
                self.__set_change_metadata__(data_metadata[hdu1.name], data_change)                
                
            cprint(__modulename__, 'Saving metadata describing data changes')
            metadata = {'headers': header_metadata, 'data': data_metadata}
            outfile = self.save(compare_id, file1, file2, metadata)
            cprint(__modulename__, 'Change analysis saved in {}'.format(outfile))
            

        hdulist1.close()
        hdulist2.close()


    def has_change(self, change):
        return (len(change.modified) > 0 or len(change.added) > 0 or len(change.deleted) > 0)


    def __get_hdu_shape__(self, hdu):
        dims = hdu._summary()[4]
        if not isinstance(hdu, fits.hdu.table.TableHDU):
            return hdu.data.shape
        else:
            row_col = dims.replace('R', '').replace('C', '').split(' x ')
            dims = (int(row_col[0]), int(row_col[1]))
            return dims

    '''
    transforms a FITS file data into Deduce records
    '''
    def __transform_hdu__(self, hdu):
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


    def __transform_image__(self, image_file):
        img = fabio.open(image_file)
        header_record_list = []
        data_record_list = []
        for k, v in img.header.items():
            header_record_list.append('{}: {}'.format(k, v))

        data_dims = img.data.shape
        if len(data_dims) == 2: # 2-D array
            for row in img.data:
                data_record_list.append(row.tolist())
        else: # n-D array 
            for row in img.data:
                flat_data = self.__flatten_ndarray__(row)
                data_record_list.append(flat_data.tolist())

        return header_record_list, data_record_list


    def __flatten_ndarray__(self, ndarray):
        if type(ndarray) == numpy.ndarray:
            flat_array = ndarray.flatten()
            flat_array = flat_array.tolist()
            return flat_array
        else:
            array = numpy.asarray(ndarray)
            flat_array = []
            for row in array:
                '''
                for col in row:
                    flat_array.append(col)
                '''
                flat_array.append(repr(row))

            flat_array = numpy.asarray(flat_array)
            return flat_array


    def __set_change_metadata__(self, metadata, change):
        metadata['counts'] = change.get_change_map()
        # REMOVED: change_factor, as it is not a useful change metric 
        #metadata['change_factor'] = change.degree


    def save(self, compare_id, old_file, new_file, metadata):
        diff_metadata = {}
        diff_metadata['analyzer'] = 'deduce::Analyzer()'
        diff_metadata['versions'] = {'base': old_file, 'revision': new_file}
        for meta in metadata:
            diff_metadata[meta] = metadata[meta]
        #diff_metadata['headers'] = header_metadata
        #diff_metadata['data'] = data_metadata
        #metafile = os.path.join(outdir, 'diff.meta')
        metafile = 'diff_{}.yml'.format(compare_id)
        dacman_utils.dump_yaml(diff_metadata, metafile)
        return metafile


    def display(self, title, edit_list):
        added = 0
        deleted = 0
        modified = 0
        unchanged = 0
        for elem in edit_list:
            if elem == 1:
                added += 1
            elif elem == 0.5:
                modified += 1
            elif elem == 0:
                unchanged += 1
            elif elem == -1:
                deleted += 1

        cprint(__modulename__, "Total Change ({}):".format(title))
        #print("Added: {}, Deleted: {}, Modified: {}, Unchanged: {}".format(added,
        print("Additions: {}, Deletions: {}, Modifications: {}, Unchanged: {}".format(added,
                                                                           deleted,
                                                                           modified,
                                                                           unchanged))
        
    '''
    def display(self, change, verbose=False):
        print("Added: {}, Deleted: {}, Modified: {}, Unchanged: {}".format(len(change.added),
                                                                           len(change.deleted),
                                                                           len(change.modified),
                                                                           len(change.unchanged)))
        if verbose:
            print("Modified records: {}".format(change.modified))
        print("Degree change: {}".format(change.degree))
    '''


    def compare(self, record_list1, record_list2):
        nrecs1 = len(record_list1)
        nrecs2 = len(record_list2)
        added = []
        deleted = []
        modified = []
        unchanged = []
        if nrecs1 < nrecs2:
            n_add = nrecs2 - nrecs1
            nrecs = nrecs1
            edit_list = record_list2[:]
            edit_list[nrecs1:nrecs2] = [1] * n_add
            for rec in record_list2[nrecs1:nrecs2]:
                added.append(rec)
        elif nrecs1 > nrecs2:
            n_del = nrecs1 - nrecs2
            nrecs = nrecs2
            edit_list =record_list1[:]
            edit_list[nrecs2:nrecs1] = [1] * n_del
            for rec in record_list1[nrecs2:nrecs1]:
                deleted.append(rec)
        else:
            nrecs = nrecs1
            edit_list =record_list1[:]
        for i in range(nrecs):
            data1 = record_list1[i]
            data2 = record_list2[i]
            if str(data1) == str(data2):
                edit_list[i] = 0
                unchanged.append(data1)
            else:
                edit_list[i] = 0.5
                modified.append(data1)
                
        change = Change(added, deleted, modified, unchanged)
        change.calculate_degree()
        return change, edit_list


    '''
    algorithm to compare arbitrary data sequences
    '''
    def compare2(self, record_list1, record_list2):
        edit_list = record_list1[:]
        added=0
        deleted=0
        modified=0
        unchanged=0
        matcher = difflib.SequenceMatcher(None, record_list1, record_list2, autojunk=False)
        for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
            if tag == 'delete':
                deleted += (i2-i1)
                #del record_list1[i1:i2]
                edit_list[i1:i2] = [-1] * (i2-i1)
            elif tag == 'equal':
                unchanged += (i2-i1)
                edit_list[i1:i2] = [0]* (i2-i1)
            elif tag == 'insert':
                added += (j2-j1)
                #record_list1[i1:i2] = record_list2[j1:j2]
                edit_list[i1:i2] = [1] * (j2-j1)
            elif tag == 'replace':
                modified += (i2-i1)
                #record_list1[i1:i2] = record_list2[j1:j2]
                edit_list[i1:i2] = [0.5] * (i2-i1)
        
        '''
        print("Added: {}, Deleted: {}, Modified: {}, Unchanged: {}".format(added,
                                                                           deleted,
                                                                           modified,
                                                                           unchanged))
        '''
        return edit_list

    '''
    The actual diff algorithm (curently uses checksums for comparing records: NOT CORRECT)
    - use Myer's diff algorithm to compare the two lists of records
    '''
    '''
    def compare(self, record_list1, record_list2):
        added = []
        modified = []
        deleted = []
        unchanged = []

        nrec1 = len(record_list1)
        nrec2 = len(record_list2)
        if nrec1 < nrec2:
            records1 = record_list1
            records2 = record_list2
        else:
            records1 = record_list2
            records2 = record_list1

        index = 0
        
        checksum_hash = {}
        for record in records1:
            checksum = hashlib.md5()
            checksum.update(repr(record))
            checksum_hash[checksum.hexdigest()] = index
            index += 1

        index = 0
        next_index = 0
        for record in records2:
            checksum = hashlib.md5()
            checksum.update(repr(record))
            checksum_val = checksum.hexdigest()
            if checksum_val in checksum_hash:
                unchanged.append(index)
                next_index = checksum_hash[checksum_val] + 1
            else:
                if index == next_index:
                    modified.append(index)
                    next_index = index + 1
                    change.modifications.append(index)
                elif index < next_index:
                    deleted.append(index)
                else:
                    added.append(index)
                    next_index = index + 1
                
            index += 1

        change = Change(added, deleted, modified, unchanged)
        return change
    '''

if __name__ == '__main__':
    file1 =sys.argv[1]
    file2 =sys.argv[2]

    cal = Analyzer()
    cal.analyze(file1, file2)
