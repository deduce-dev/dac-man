"""
`dacman.core.comparator`
====================================

.. currentmodule:: dacman.core.comparator

:platform: Unix, Mac
:synopsis: Module called from change.py to do the actual comparison

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

import sys
import os
import uuid

import dacman.core.indexer as indexer
from dacman.core.utils import cprint, get_hash_id
import dacman.core.utils as dacman_utils

import logging

__modulename__ = 'comparator'

def get_index_data(index_file):
    index_data = {}
    with open(index_file) as f:
        lines = f.readlines()
        for line in lines:
            kv = line.split(':')
            index_data[kv[0].strip()] = kv[1].strip()
    return index_data

'''
Function to compare data and find changes
Algo:
- for filepaths in NEW_PATH_INDEX:
 - if filepaths match between NEW_PATH_INDEX and OLD_PATH_INDEX, then:
   -- if datahashes match, then add to unchanged
   -- else, add to modified
   -- remove from OLD_PATH_INDEX
 - else if filename is found in OLD_NAME_PATHS (but paths differ), then:
   -- get all associated filepaths from OLD_NAME_PATHS (and associated datahashes)
   -- for all these filepaths:
     --- if datahashes match between NEW_PATH_INDEX and OLD_PATH_INDEX, then unchanged
        ---- remove it from OLD_PATH_INDEX, and break
  -- if no datahash match has been found
     --- select the first filepath, mark it modified
     --- remove it from OLD_PATH_INDEX and OLD_NAME_PATHS
 - else (no matching path or filename):
   -- if datahashes match to any OLD_DATA_INDEX, then add to unchanged
     --- remove it from OLD_PATH_INDEX and OLD_DATA_INDEX
   -- else, add to added
- for all remaining filepaths in OLD_PATH_INDEX:
   -- add to deleted
'''
def compare(old_datapath, new_datapath, custom_stagingdir):
    logger = logging.getLogger(__name__)

    logger.info('Starting directory comparison')
    if not custom_stagingdir:        
        #old_stagingdir = os.path.join(old_datapath, '.deduce')
        stagingdir = dacman_utils.DACMAN_STAGING_LOC
    else:
        stagingdir = custom_stagingdir

    old_indexdir = os.path.join(stagingdir, 'indexes', get_hash_id(old_datapath))
    new_indexdir = os.path.join(stagingdir, 'indexes', get_hash_id(new_datapath))

    old_index_file = os.path.join(old_indexdir, 'PATH.idx')
    new_index_file = os.path.join(new_indexdir, 'PATH.idx')
    
    if not os.path.exists(old_index_file):
        indexer.index(old_datapath, stagingdir)
    if not os.path.exists(new_index_file):
        indexer.index(new_datapath, stagingdir)

    old_data_index_file = os.path.join(old_indexdir, 'DATA.idx')
    old_pathname_map_file = os.path.join(old_indexdir, 'PATHNAME.map')

    old_metafile = os.path.join(old_indexdir, 'METADATA')
    new_metafile = os.path.join(new_indexdir, 'METADATA')

    #cprint(__modulename__, 'Loading Indexes')
    logger.info('Loading indexes for fast comparison')
    old_path_indexes = dacman_utils.file_to_dict(old_index_file)
    new_path_indexes = dacman_utils.file_to_dict(new_index_file)
    old_data_indexes = dacman_utils.file_to_dict(old_data_index_file)
    name_path_map = dacman_utils.file_to_dict_list(old_pathname_map_file)

    old_metadata = dacman_utils.file_to_dict(old_metafile)
    new_metadata = dacman_utils.file_to_dict(new_metafile)

    _unchanged = []
    _metachange = {}
    _added = []
    _deleted = []
    _modified = {}
    
    #cprint(__modulename__, 'Comparing {} and {}'.format(old_datapath, new_datapath))

    # MD5 hash for a zero-byte file
    __MAGIC_HASH__ = 'd41d8cd98f00b204e9800998ecf8427e'

    logger.info('Comparing files in %s and %s', old_datapath, new_datapath)
    for filepath in new_path_indexes:
        datahash = new_path_indexes[filepath]
        if filepath in old_path_indexes:
            '''
            if filepaths are same, but data or metadata changed
            '''
            if datahash == old_path_indexes[filepath]:
                if filepath in old_metadata and filepath in new_metadata:
                    if old_metadata[filepath] == new_metadata[filepath]:
                        _unchanged.append(filepath)
                    else:
                        _metachange[filepath] = filepath
                else:
                    _unchanged.append(filepath)
            else:
                _modified[filepath] = filepath
            old_path_indexes.pop(filepath)
            basename = os.path.basename(filepath)
            if basename in name_path_map:
                if filepath in name_path_map[basename]:
                    name_path_map[basename].remove(filepath)
                    if len(name_path_map[basename]) == 0:
                        name_path_map.pop(basename)
        elif os.path.basename(filepath) in name_path_map:
            '''
            if filenames are same, but filepaths and data changed
            '''
            filename = os.path.basename(filepath)
            old_filepaths = name_path_map[filename]
            for old_filepath in old_filepaths:
                if datahash == old_path_indexes[old_filepath]:
                    _metachange[filepath] = old_filepath
                    old_path_indexes.pop(old_filepath)
                    name_path_map[filename].remove(old_filepath)
                    break
            if filepath not in _metachange:
                old_filepath = old_filepaths[0]
                _modified[filepath] = old_filepath
                old_path_indexes.pop(old_filepath)
                del name_path_map[filename][0]
            if len(name_path_map[filename]) == 0:
                name_path_map.pop(filename)
        elif datahash in old_data_indexes and datahash != __MAGIC_HASH__:
            '''
            if data remains same, but filepath changes
            '''
            old_filepath = old_data_indexes[datahash]
            if old_filepath in old_path_indexes:
                _metachange[filepath] = old_filepath
                old_path_indexes.pop(old_filepath)
                old_data_indexes.pop(datahash)
                basename = os.path.basename(old_filepath)
                if basename in name_path_map:
                    if old_filepath in name_path_map[basename]:
                        name_path_map[basename].remove(old_filepath)
                        if len(name_path_map[basename]) == 0:
                            name_path_map.pop(basename)
            else:
                _added.append(filepath)
        else:
            _added.append(filepath)
                
    for old_filepath in old_path_indexes:
        _deleted.append(old_filepath)
    
    """
    '''
    This logic doesn't allow for multiple files in the same directory
    structure to have the same data (YAML would raise duplicate key error).
    The first loop identifes matches between the old and new data.
    The second loop identifies the data that are added in new. 
    '''
    for index in old_data_indexes:
        old_data_name = old_data_indexes[index]
        '''
        if the contents of two files are same, then they are unchanged
        even if their names changed
        '''
        if index in new_data_indexes:
            new_data_name = new_data_indexes.pop(index)
            _unchanged[new_data_name] = old_data_name            
            base_new_data = os.path.basename(new_data_name)
            path_indexes = new_name_indexes[base_new_data]
            path_indexes.pop(new_data_name)
            if len(new_name_indexes[base_new_data]) == 0:
                new_name_indexes.pop(base_new_data)
        else:
            '''
            - if the file and directory remain same, but contents changed, 
              then it's a modification
            - if a file with the same name is present (can be under a
              different directory), but the contents changed
              then it's a modification 
            - else a deletion
            '''
            base_old_data = os.path.basename(old_data_name)
            if base_old_data in new_name_indexes:
                #_modified[old_name_indexes[old_data_name]] = new_name_indexes[old_data_name]
                #_modified[new_name_indexes[old_data_name]] = old_name_indexes[old_data_name]
                path_indexes = new_name_indexes[base_old_data]
                if old_data_name in path_indexes:
                    data_hash = path_indexes.pop(old_data_name)
                    new_data_name = new_data_indexes.pop(data_hash)
                else:
                    path, data_hash = path_indexes.popitem()
                    new_data_name = new_data_indexes.pop(data_hash)
                #data_hash = new_name_indexes[base_old_data]
                #new_data_name = new_data_indexes.pop(data_hash)                
                _modified[new_data_name] = old_data_name
                if len(new_name_indexes[base_old_data]) == 0:
                    new_name_indexes.pop(base_old_data)
            else:
                _deleted.append(old_data_name)            
            
    for index in new_data_indexes:
        _added.append(new_data_indexes[index])

    """

    #cprint(__modulename__, 'Calculating change')        
    #logger.info('Calculating metrics for quantifying changes')
    #change_file = os.path.join(new_stagingdir, 'CHANGE')
    #change_id = str(uuid.uuid4())
    '''
    Saving change information in cache
    '''
    logger.info('Updating change cache entries')
    change_id = dacman_utils.hash_comparison_id(old_datapath, new_datapath)
    cachedir = os.path.join(stagingdir, 'cache')
    if not os.path.exists(cachedir):
        os.makedirs(cachedir)
    change_file = os.path.join(cachedir, 'ENTRIES')
    change_info = {new_datapath : {old_datapath: change_id}}
    dacman_utils.update_yaml(change_info, change_file)

    logger.info('Saving change measurements')

    change_dir = os.path.join(cachedir, change_id)
    if not os.path.exists(change_dir):
        os.makedirs(change_dir)

    _meta_info = {'base': {'dataset_id': old_datapath,
                           'nfiles': dacman_utils.get_nfiles(old_datapath, stagingdir)},
                  'revision': {'dataset_id': new_datapath,
                               'nfiles': dacman_utils.get_nfiles(new_datapath, stagingdir)}}
    _metafile = os.path.join(change_dir, 'META_INFO')
    _ufile = os.path.join(change_dir, 'UNCHANGED')
    _afile = os.path.join(change_dir, 'ADDED')
    _dfile = os.path.join(change_dir, 'DELETED')
    _mfile = os.path.join(change_dir, 'MODIFIED')
    _mcfile = os.path.join(change_dir, 'METACHANGE')
    dacman_utils.dump_yaml(_meta_info, _metafile)
    dacman_utils.list_to_file(_unchanged, _ufile)
    dacman_utils.list_to_file(_added, _afile)
    dacman_utils.list_to_file(_deleted, _dfile)
    dacman_utils.dict_to_file(_modified, _mfile)
    dacman_utils.dict_to_file(_metachange, _mcfile)

    logger.info('Directory comparison complete')

    return change_id
         

def main(args):
    oldpath = os.path.abspath(args['oldpath'])
    newpath = os.path.abspath(args['newpath'])
    stagingdir = args['stagingdir']

    compare(oldpath, newpath, stagingdir)

if __name__ == '__main__':
   args = {'oldpath': sys.argv[1], 'newpath': sys.argv[2]}

   main(args)
