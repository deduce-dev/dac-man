"""
`dacman.core.change`
====================================

.. currentmodule:: dacman.core.change

:platform: Unix, Mac
:synopsis: Module to capture changes between datasets

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

try:
   from os import scandir, walk
except ImportError:
   from scandir import scandir, walk

import yaml
import sys
import os
import uuid
import shutil

import dacman.core.scanner as scanner
import dacman.core.indexer as indexer
import dacman.core.comparator as comparator
from dacman.core.utils import cprint, get_hash_id
import dacman.core.utils as dacman_utils

import logging

__modulename__ = 'change'

'''
base class that captures change in terms of number of objects added, deleted, modified, unchanged
'''
class Change():
    def __init__(self, added, deleted, modified, unchanged):
        self._added = added
        self._deleted = deleted
        self._modified = modified
        self._unchanged = unchanged
        '''
        the degree of total change in the dataset
        '''
        self._degree = 0.0

    @property
    def old_path(self):
        return self._old_path

    @property
    def new_path(self):
        return self._new_path

    @property
    def old_nfiles(self):
        return self._old_nfiles

    @property
    def new_nfiles(self):
        return self._new_nfiles

    @property
    def added(self):
        return self._added

    @property
    def deleted(self):
        return self._deleted

    @property
    def modified(self):
        return self._modified

    @property
    def unchanged(self):
        return self._unchanged

    @property
    def degree(self):
        return self._degree

    def calculate_degree(self):
       total_change = len(self.added) + len(self.deleted) + len(self.modified)
       total_original_data = len(self.deleted) + len(self.modified) + len(self.unchanged)

       if total_original_data > 0:
          self._degree = total_change * 1.0 / total_original_data
       else:
          self._degree = 100.0
       return self._degree

    def get_change_map(self):
       change_map = {'modified': len(self._modified),
                     'deleted': len(self._deleted),
                     'added': len(self._added),
                     'unchanged': len(self._unchanged)}       
       return change_map

#################

class FilesystemChange(Change):
    def __init__(self, old_path, new_path, old_deducedir, new_deducedir):
        Change.__init__(self, [], [], [], [])
        self._old_path = old_path
        self._new_path = new_path
        self._old_nfiles = self.__get_nfiles__(old_deducedir)
        self._new_nfiles = self.__get_nfiles__(new_deducedir)
        self._metachange = []

    def __get_nfiles__(self, deducedir):
        deduce_file = os.path.join(deducedir, 'FILEPATHS')
        with open(deduce_file) as f:
           nlines = sum(1 for line in f)
        return nlines

    def add_changes(self, added=[], deleted=[], modified=[], unchanged=[], metachange=[]):
        self._added = added
        self._deleted = deleted
        self._modified = modified
        self._unchanged = unchanged
        self._metachange = metachange

    @property
    def old_path(self):
        return self._old_path

    @property
    def new_path(self):
        return self._new_path

    @property
    def old_nfiles(self):
        return self._old_nfiles

    @property
    def new_nfiles(self):
        return self._new_nfiles

    @old_nfiles.setter
    def old_nfiles(self, old_nfiles):
        self._old_nfiles = old_nfiles

    @new_nfiles.setter
    def new_nfiles(self, new_nfiles):
        self._new_nfiles = new_nfiles

    @property
    def metachange(self):
        return self._metachange

    def calculate_degree(self):
       total_change = len(self.added) + len(self.deleted) + len(self.modified)
       total_original_data = len(self.deleted) + len(self.modified) +\
           len(self.metachange) + len(self.unchanged)

       if total_original_data > 0:
          self._degree = total_change * 1.0 / total_original_data
       else:
          self._degree = 100.0
       return self._degree

    def get_change_map(self):
       change_map = {'modified': len(self._modified),
                     'deleted': len(self._deleted),
                     'added': len(self._added),
                     'metaonly': len(self._metachange),
                     'unchanged': len(self._unchanged)}       
       return change_map


######################################################################################
'''
utility function to find directory entries
'''
def find_direntries(dir):
    entries = {}
    if not os.path.exists(dir):
       cprint(__modulename__, 'Directory {} does not exist'.format(dir))
       sys.exit()

    for entry in scandir(dir):
        entries[entry.name] = entry
    return entries
    

'''
(deprecated) utility function to find the path where .deduce directory exists
'''
def find_deduce(datapath):
    relative_datadir = ''
    rootdir = '/'

    olddir_ = datapath
    deducedir = os.path.join(datapath, '.deduce')
    if not os.path.exists(deducedir):
       deducedir = None
    
    '''
    get to the topmost directory where .deduce exists
    - this is to ensure consistent diff results once parent directories are deduce'd
    - else, deduce diff (for the first time) an inner directory first and then the
      parent directory, would result in inconsistent diff results 
    '''
    while olddir_ != rootdir:
       parent_dir = os.path.dirname(olddir_)
       cur_dir = os.path.basename(olddir_)
       '''
       save the relative path from deduce-dir to the specified data directory,
       might be used when fetching and displaying changes
       '''
       relative_datadir = os.path.join(cur_dir, relative_datadir)
       entries = find_direntries(parent_dir)
       if '.deduce' in entries:
          deducedir = os.path.join(parent_dir, '.deduce')
       olddir_ = parent_dir

    return deducedir

'''
initialize deduce for a datapath: if already indexed by deduce then return the deduce directory
else index the datapath and return
'''
def init_deduce(datapath, custom_deducedir):
   if not custom_deducedir:        
      #deducedir = find_deduce(datapath)
      #deducedir = os.path.join(os.getenv('HOME'), '.dacman', get_hash_id(datapath))
      deducedir = os.path.join(dacman_utils.DACMAN_STAGING_LOC, get_hash_id(datapath))
   else:
      deducedir = os.path.join(custom_deducedir, get_hash_id(datapath))

   indexdir = os.path.join(deducedir, 'indexes')
   if not os.path.exists(indexdir):
      deducedir = indexer.index(datapath, os.path.dirname(deducedir))

   return deducedir


'''
find the high-level changes between two paths
- if indexed and compared, then just fetch the comparison data
- else scan and index all the data sets (files/directories) recursively
'''
#def changes(old_path, new_path, custom_old_deducedir=None, custom_new_deducedir=None):
def changes(old_datapath, new_datapath, custom_deducedir=None):
    logger = logging.getLogger(__name__)

    #old_datapath = os.path.abspath(old_path)
    #new_datapath = os.path.abspath(new_path)

    if old_datapath == new_datapath:
       logger.error('Comparison paths are the same')
       sys.exit()

    if not custom_deducedir:
       deducedir = dacman_utils.DACMAN_STAGING_LOC
    else:
       deducedir = custom_deducedir
    old_deducedir = init_deduce(old_datapath, custom_deducedir)
    new_deducedir = init_deduce(new_datapath, custom_deducedir)

    '''
    vars that contain the actual datapaths where indexing was done
    '''
    old_deducepath = ''
    new_deducepath = ''

    datapath_info = os.path.join(old_deducedir, 'DATAPATH')
    abs_old_path = '{}/'.format(os.path.abspath(old_datapath))
    if not os.path.exists(datapath_info):
        scanner.scan(old_datapath, custom_deducedir)
    with open(datapath_info) as f:
       old_deducepath = f.readline().strip()
       old_retrieved_datapath = '{}/'.format(old_deducepath)
       if old_retrieved_datapath not in abs_old_path:
          #cprint(__modulename__, 'Datapath `{}` is not a valid, indexed datapath!'.format(abs_old_path))
          logger.error('%s is not a valid, indexed datapath!', abs_old_path)
          sys.exit()

    datapath_info = os.path.join(new_deducedir, 'DATAPATH')
    abs_new_path = '{}/'.format(os.path.abspath(new_datapath))
    if not os.path.exists(datapath_info):
        scanner.scan(new_datapath, custom_deducedir)
    with open(datapath_info) as f:        
       new_deducepath = f.readline().strip()
       new_retrieved_datapath = '{}/'.format(new_deducepath)
       if new_retrieved_datapath not in abs_new_path:
          #cprint(__modulename__, 'Datapath `{}` is not a valid, indexed datapath!'.format(abs_new_path))
          logger.error('%s is not a valid, indexed datapath!', abs_new_path)
          sys.exit()
    
    
    change_dir = ''
    deducepath = new_datapath # default prefix to search for diff data; will be updated if only subdirs are diff'd
    #is_subdir = False # true, if the diff is for some data inside the subdirectories
    is_subdir_oldpath = False
    is_subdir_newpath = False
    deduce_change = os.path.join(new_deducedir, 'CHANGE')

    #cprint(__modulename__, 'Retrieving change between {} and {}'.format(old_datapath,
    #                                                                    new_datapath))

    logger.info('Checking for changes between %s and %s', old_datapath, new_datapath)

    '''
    if no high-level diff exists for the data, the do a comparison
    - do the comparison for the all the indexed data
    - at runtime, decide is the comparison is between any subdirectories of the total diff
    '''
    if not os.path.exists(deduce_change):
        logger.info('Changes are not pre-calculated, directories have to be compared')
        change_dir = comparator.compare(old_deducepath, new_deducepath, deducedir)
    else:
        logger.info('Changes are already calculated')
        '''
        if the high-level diff exists, then check if it exists for the two data versions provided here
        '''
        with open(deduce_change, 'r') as f:
            change_info = yaml.load(f)
            '''
            if the diff path is where deduce indexing (deduce path) was done
            '''
            if new_datapath in change_info:
               '''
               if the diff paths are already compared, then get the corresponding directory;
               else, do the comparisons/diff
               '''
               if old_datapath in change_info[new_datapath]:
                  '''
                  if both oldpath and newpath are in resp. deduce paths
                  '''
                  change_dir = change_info[new_datapath][old_datapath]
               else:
                  '''
                  if the oldpath is a subdirectory, and the newpath is in deduce path
                  '''
                  for o in change_info[new_datapath]:
                     parent_path = o + os.sep
                     if old_datapath.startswith(parent_path):
                        change_dir = change_info[new_datapath][o]
                        break

                  '''
                  if the oldpath is neither a deduce path nor a subdir, then it's a new comparison
                  '''
                  if change_dir == '':
                     '''
                     if the deduce paths are custom paths, then there exists only one deduce dir
                     and hence, needs to be deleted as the previous indexes were on subdirectories
                     of the queried path (needs to be recalculated from the beginning)
                     '''
                     if custom_new_deducedir:
                        shutil.rmtree(new_deducedir)
                     change_dir = comparator.compare(old_deducepath, new_deducepath, deducedir)
            elif new_deducepath in change_info:
               '''
               if the datapaths are not compared, but the corr deducepaths are,
               then the datapaths are subdirectories and changes can be derived
               from the deducepath changes
               '''
               if old_deducepath in change_info[new_deducepath]:
                  change_dir = change_info[new_deducepath][old_deducepath]
               else:
                  change_dir = comparator.compare(old_deducepath, new_deducepath, deducedir)
            else:
               '''
               if neither the datapath nor the deducepaths are in changeinfo,
               then there's something wrong
               '''
               #cprint(__modulename__, 'The deducedir only contains changes used for {}'.format(new_deducepath))
               logger.error('Indexes do not match the data directory; re-indexing required')
               sys.exit()
            #print('CHANGEDIR: {}'.format(change_dir))       

    if old_deducepath != old_datapath:
       is_subdir_oldpath = True

    if new_deducepath != new_datapath:
       is_subdir_newpath = True

    logger.info('Retrieving changes between %s and %s', old_datapath, new_datapath)

    change = FilesystemChange(old_datapath, new_datapath, old_deducedir, new_deducedir)

    change_data_dir = os.path.join(new_deducedir, 'changes', change_dir)
    if not (is_subdir_oldpath or is_subdir_newpath):
       set_change_from_cache(change, change_data_dir)
    else:
       compare_hash = dacman_utils.hash_comparison_id(old_datapath, new_datapath)
       change_data_subdir = os.path.join(change_data_dir, compare_hash)
       if os.path.exists(change_data_subdir):
          set_change_from_cache(change, change_data_subdir)
       else:
          save_subdir_changes_to_cache(change, old_deducepath, new_deducepath,
                                       old_datapath, new_datapath,
                                       is_subdir_oldpath, is_subdir_newpath,
                                       change_data_dir, change_data_subdir)

    if is_subdir_newpath:
       subdir_nfiles = get_subdir_nfiles(new_datapath, new_deducedir)
       change.new_nfiles = subdir_nfiles
       #print("Subdir files: {}".format(subdir_nfiles))

    if is_subdir_oldpath:
       subdir_nfiles = get_subdir_nfiles(old_datapath, old_deducedir)
       change.old_nfiles = subdir_nfiles

    '''
    _added = collect_list(deducepath, new_datapath, change_data_dir, is_subdir, 'ADDED')
    _deleted = collect_list(deducepath, new_datapath, change_data_dir, is_subdir, 'DELETED')
    _modified = collect_dict(deducepath, new_datapath, change_data_dir, is_subdir, 'MODIFIED')
    _metachange = collect_dict(deducepath, new_datapath, change_data_dir, is_subdir, 'METACHANGE')
    _unchanged = collect_list(deducepath, new_datapath, change_data_dir, is_subdir, 'UNCHANGED')
    '''
    #change = Change(_added, _deleted, _modified, _unchanged, _metachange)

    #cprint(__modulename__, 'Retrieved change information')
    logger.info('Change retrieval completed')

    return change


def get_subdir_nfiles(datapath, deducedir):
   paths_file = os.path.join(deducedir, 'FILEPATHS')
   datapath_file = os.path.join(deducedir, 'DATAPATH')
   deducepath = ''
   with open(datapath_file) as f:
      deducepath = f.readline().strip()

   nfiles = 0
   with open(paths_file) as f:
      for path in f:
         abspath = os.path.join(deducepath, path)
         if abspath.startswith(datapath):
            nfiles += 1

   return nfiles


'''
if change is already calcualted, just retrieve it
'''
def set_change_from_cache(change, change_dir):
   change_types = {'ADDED': list, 'DELETED': list, 
                   'MODIFIED': dict, 'METACHANGE': dict,
                   'UNCHANGED': list}
   change_data = {}
   for change_type in change_types:
      change_file = os.path.join(change_dir, change_type)
      if change_types[change_type] == list:
         with open(change_file, 'r') as f:
            lines = f.readlines()
            change_data[change_type] = [line.strip() for line in lines]
      else:
         with open(change_file, 'r') as f:
            change_dict = {}
            for line in f:
               kv = line.split(':')
               change_dict[kv[0]] = kv[1].strip()
            change_data[change_type] = change_dict

   change.add_changes(change_data['ADDED'], change_data['DELETED'],
                      change_data['MODIFIED'], change_data['UNCHANGED'],
                      change_data['METACHANGE'])
   change.calculate_degree()
   

def display(change):
    #cprint(__modulename__,
    #       "Added: {}, Deleted: {}, Modified: {}, Metachange: {}, Unchanged: {}".
    #       format(len(change.added),
    #              len(change.deleted),
    #              len(change.modified),
    #              len(change.metachange),
    #              len(change.unchanged)))
    #cprint(__modulename__, "Degree change: {}".format(change.degree))
    #print("Added: {}, Deleted: {}, Modified: {}, Metadata: {}, Unchanged: {}".
    print("Additions: {}, Deletions: {}, Modifications: {}, Metadata changes: {}, Unchanged: {}".
          format(len(change.added),
                 len(change.deleted),
                 len(change.modified),
                 len(change.metachange),
                 len(change.unchanged)))
    # REMOVED: degree change, as it is not a useful change metric
    #print("Degree change: {}".format(change.degree))


'''
derives subdirectory-level changes
'''
def save_subdir_changes_to_cache(change, old_deducepath, new_deducepath,
                                 old_datapath, new_datapath,
                                 is_subdir_oldpath, is_subdir_newpath,
                                 change_dir, change_subdir):
   change_data = {'ADDED': [], 'DELETED': [],
                  'MODIFIED': {}, 'METACHANGE': {},
                  'UNCHANGED': []}

   cprint(__modulename__, 'Subdirectory level changes not cached. Calculating and caching the changes')
   if is_subdir_oldpath and not is_subdir_newpath:
      '''
      if oldpath is a subdir of the deducepath, then mark all the files that are
      not in oldpath as added w.r.t the newpath
      '''
      for change_type in change_data:
         base_change_file = os.path.join(change_dir, change_type)
         if change_type == 'ADDED':
            with open(base_change_file) as f:
               lines = f.readlines()
               change_data[change_type] = [line.strip() for line in lines]
         if change_type == 'DELETED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(old_deducepath, line.strip())
                  if path.startswith(old_datapath):
                     rel_subpath = os.path.relpath(path, old_datapath)               
                     change_data[change_type].append(rel_subpath)
               lines = f.readlines()
               change_data[change_type] = [line.strip() for line in lines]
         elif change_type == 'UNCHANGED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(old_deducepath, line.strip())
                  if path.startswith(old_datapath):
                     '''
                     there's nothing unchanged anymore, everything is metachange
                     because the directory depths have changed and so have the relative
                     file paths
                     '''
                     #change_data[change_type].append(line.strip())
                     rel_subpath = os.path.relpath(path, old_datapath)               
                     change_data['METACHANGE'][line.strip()] = rel_subpath
                  else:
                     change_data['ADDED'].append(line.strip())
         elif change_type == 'METACHANGE':
            with open(base_change_file) as f:
               for line in f:
                  kv = line.split(':')
                  path = os.path.join(old_deducepath, kv[1].strip())
                  if path.startswith(old_datapath):
                     rel_subpath = os.path.relpath(path, old_datapath)
                     if kv[0] == rel_subpath: # if the filepath is now at the same level, then unchanged
                        change_data['UNCHANGED'].append(rel_subpath)
                     else:
                        change_data[change_type][kv[0]] = rel_subpath
                  else:
                     change_data['ADDED'].append(kv[0])            
         else:
            with open(base_change_file) as f:
               for line in f:
                  kv = line.split(':')
                  path = os.path.join(old_deducepath, kv[1].strip())
                  if path.startswith(old_datapath):
                     rel_subpath = os.path.relpath(path, old_datapath)
                     change_data[change_type][kv[0]] = rel_subpath
                  else:
                     change_data['ADDED'].append(kv[0])
   elif not is_subdir_oldpath and is_subdir_newpath:
      '''
      if newpath is a subdir of the deducepath, then mark all the files that are
      not in newpath as deleted
      '''
      for change_type in change_data:
         base_change_file = os.path.join(change_dir, change_type)
         if change_type == 'ADDED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(new_deducepath, line.strip())
                  if path.startswith(new_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)               
                     change_data[change_type].append(rel_subpath)            
         elif change_type == 'DELETED':
            with open(base_change_file) as f:
               lines = f.readlines()
               change_data[change_type] = [line.strip() for line in lines]
         elif change_type == 'UNCHANGED':
            with open(base_change_file) as f:
               for line in f:
                  orig_path = line.strip()
                  path = os.path.join(new_deducepath, orig_path)
                  if path.startswith(new_datapath):
                     #change_data[change_type].append(rel_subpath)
                     rel_subpath = os.path.relpath(path, new_datapath)
                     change_data['METACHANGE'][rel_subpath] = orig_path
                  else:
                     change_data['DELETED'].append(orig_path)
         elif change_type == 'METACHANGE':
            with open(base_change_file) as f:
               for line in f:
                  kv = line.split(':')
                  path = os.path.join(new_deducepath, kv[0])
                  old_path = kv[1].strip()
                  if path.startswith(new_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)
                     if rel_subpath == old_path:
                        change_data['UNCHANGED'].append(rel_subpath)
                     else:
                        change_data[change_type][rel_subpath] = old_path
                  else:
                     change_data['DELETED'].append(old_path)            
         else:
            with open(base_change_file) as f:
               for line in f:
                  kv = line.split(':')
                  path = os.path.join(new_deducepath, kv[0])
                  if path.startswith(new_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)
                     change_data[change_type][rel_subpath] = kv[1].strip()
                  else:
                     change_data['DELETED'].append(kv[1].strip())
   else:
      '''
      if both oldpath and newpath are subdirs, then only compare the
      files that match both the paths
      '''
      for change_type in change_data:
         base_change_file = os.path.join(change_dir, change_type)
         if change_type == 'ADDED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(new_deducepath, line.strip())
                  if path.startswith(new_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)
                     change_data[change_type].append(rel_subpath)
         elif change_type == 'DELETED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(old_deducepath, line.strip())
                  if path.startswith(old_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)
                     change_data[change_type].append(rel_subpath)
         elif change_type == 'UNCHANGED':
            with open(base_change_file) as f:
               for line in f:
                  orig_path = line.strip()
                  path = os.path.join(new_deducepath, orig_path)
                  old_path = os.path.join(old_deducepath, orig_path)
                  if path.startswith(new_datapath): # if the path is in new_datapath
                     rel_subpath = os.path.relpath(path, new_datapath)
                     if old_path.startswith(old_datapath): # if the path is in old_datapath
                        rel_old_subpath = os.path.relpath(old_path, old_datapath)
                        # if the two relative paths are same, then unchanged
                        if rel_subpath == rel_old_subpath: 
                           change_data[change_type].append(rel_subpath)                     
                        else:
                           change_data['METACHANGE'][rel_subpath] = rel_old_subpath
                     else:
                        change_data['ADDED'].append(rel_subpath)
                  elif old_path.startswith(old_datapath): # if the path is not in new_datapath, but in old_datapath
                     rel_old_subpath = os.path.relpath(old_path, old_datapath)
                     change_data['DELETED'].append(rel_old_subpath)
         elif change_type == 'METACHANGE':
            with open(base_change_file) as f:
               for line in f:
                  kv = line.split(':')
                  orig_new_path = kv[0]
                  orig_old_path = kv[1].strip()
                  path = os.path.join(new_deducepath, orig_new_path)
                  old_path = os.path.join(old_deducepath, orig_old_path)
                  if path.startswith(new_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)
                     if old_path.startswith(old_datapath):
                        rel_old_subpath = os.path.relpath(old_path, old_datapath)
                        if rel_subpath == rel_old_subpath:
                           change_data['UNCHANGED'].append(rel_subpath)
                        else:
                           change_data[change_type][rel_subpath] = rel_old_subpath
                     else:
                        change_data['ADDED'].append(rel_subpath)
                  elif old_path.startswith(old_datapath):
                     rel_old_subpath = os.path.relpath(old_path, old_datapath)
                     change_data['DELETED'].append(rel_old_subpath)
         else:
            with open(base_change_file) as f:
               for line in f:
                  kv = line.split(':')
                  orig_new_path = kv[0]
                  orig_old_path = kv[1].strip()
                  path = os.path.join(new_deducepath, orig_new_path)
                  old_path = os.path.join(old_deducepath, orig_old_path)
                  if path.startswith(new_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)
                     if old_path.startswith(old_datapath):
                        rel_old_subpath = os.path.relpath(old_path, old_datapath)                        
                        change_data[change_type][rel_subpath] = rel_old_subpath
                     else:
                        change_data['ADDED'].append(rel_subpath)
                  elif old_path.startswith(old_datapath):
                     rel_old_subpath = os.path.relpath(old_path, old_datapath)
                     change_data['DELETED'].append(rel_old_subpath)
                     
   _ufile = os.path.join(change_subdir, 'UNCHANGED')
   _afile = os.path.join(change_subdir, 'ADDED')
   _dfile = os.path.join(change_subdir, 'DELETED')
   _mfile = os.path.join(change_subdir, 'MODIFIED')
   _mcfile = os.path.join(change_subdir, 'METACHANGE')
   
   #print("CHANGEDIR: {}, CHANGESUBDIR: {}".format(change_dir, change_subdir))
   os.mkdir(change_subdir)

   dacman_utils.list_to_file(change_data['UNCHANGED'], _ufile)
   dacman_utils.list_to_file(change_data['ADDED'], _afile)
   dacman_utils.list_to_file(change_data['DELETED'], _dfile)
   dacman_utils.dict_to_file(change_data['MODIFIED'], _mfile)
   dacman_utils.dict_to_file(change_data['METACHANGE'], _mcfile)
    
   change.add_changes(change_data['ADDED'], change_data['DELETED'],
                      change_data['MODIFIED'], change_data['UNCHANGED'],
                      change_data['METACHANGE'])
   change.calculate_degree()
    
               

def collect_list(deducepath, datapath, change_dir, is_subdir, change_type):
    change_file = os.path.join(change_dir, change_type)
    with open(change_file, 'r') as f:
        change_data = f.readlines()
        change_data = [data.strip() for data in change_data]
        '''
        if the diff path is just a subdirectory of a deduce index, 
        then return only the specific diff 
        else, return the total diff between the paths
        '''
        if is_subdir_newpath:
            change_sample = []
            for path in change_data:
                abspath = os.path.join(new_deducepath, path)
                if abspath.startswith(datapath):
                    change_sample.append(path)
            return change_sample
        else:
            return change_data

def collect_dict(deducepath, datapath, change_dir, is_subdir, change_type):
    change_file = os.path.join(change_dir, change_type)
    with open(change_file, 'r') as f:
        lines = f.readlines()
        change_data = {}
        for line in lines:
           kv = line.split(':')
           change_data[kv[0]] = kv[1].strip()
        '''
        if the diff path is just a subdirectory of a deduce index, 
        then return only the specific diff 
        else, return the total diff between the paths
        '''
        if is_subdir:
            change_sample = {}
            for path in change_data:
                abspath = os.path.join(deducepath, path)
                if abspath.startswith(datapath):
                    change_sample[path] = change_data[path]
            return change_sample
        else:
            return change_data


"""
def collect(deducepath, datapath, change_dir, is_subdir, change_type):
    change_file = os.path.join(change_dir, change_type)
    with open(change_file, 'r') as f:
        change_data = yaml.load(f)
        '''
        if the diff path is just a subdirectory of a deduce index, 
        then return only the specific diff 
        else, return the total diff between the paths
        '''
        if is_subdir:
            change_sample = {}
            for path in change_data:
                abspath = os.path.join(deducepath, path)
                if abspath.startswith(datapath):
                    change_sample[path] = change_data[path]
            return change_sample
        else:
            return change_data
"""

        
def main(args):
    oldpath = os.path.abspath(args.oldpath)
    newpath = os.path.abspath(args.newpath)
    deducedir = args.stagingdir
    '''
    None, None
    if args.stagingdir is not None:
       olddeducedir = os.path.join(args.stagingdir, os.path.basename(args.oldpath))
       newdeducedir = os.path.join(args.stagingdir, os.path.basename(args.newpath))
    '''
    change = changes(oldpath, newpath, deducedir)
    display(change)

def s_main(args):
    oldpath = args['oldpath']
    newpath = args['newpath']
    deducedir = args['deducedir']

    change = changes(oldpath, newpath, deducedir)
    display(change)

if __name__ == '__main__':
   args = {'oldpath': sys.argv[1], 'newpath': sys.argv[2]}

   s_main(args)
