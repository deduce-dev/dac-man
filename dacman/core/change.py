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
    def __init__(self, old_path, new_path, stagingdir):
        Change.__init__(self, [], [], [], [])
        self._old_path = old_path
        self._new_path = new_path
        self._old_nfiles = 0
        self._new_nfiles = 0
        self._stagingdir = stagingdir
        self._metachange = []

    '''
    def __get_nfiles__(self, path):
        print(path)
        scan_file = os.path.join(self._stagingdir, 'indexes', get_hash_id(path), 'FILEPATHS')
        with open(scan_file) as f:
           nlines = sum(1 for line in f)
        return nlines

    def set_path_files(self, path):
       self._old_nfiles = self.__get_nfiles__(self._old_path)
       self._new_nfiles = self.__get_nfiles__(self._new_path)
    '''

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


class CacheStatus(object):
   ALL_CACHED = 0
   NEW_PARENT_CACHED = 1
   OLD_PARENT_CACHED = 2
   BOTH_PARENTS_CACHED = 3
   NOT_CACHED = 4

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
This will be the future way of invoking change calculation.
The module function will be removed 
'''
class ChangeManager(object):

   def __init__(self, old_datapath, new_datapath, force=False, custom_stagingdir=None):
      self._old_datapath = old_datapath
      self._new_datapath = new_datapath
      self._force = force
      if not custom_stagingdir:
         self._stagingdir = dacman_utils.DACMAN_STAGING_LOC
      else:
         self._stagingdir = custom_stagingdir

      self._cachedir = os.path.join(self._stagingdir, 'cache')
      self._cache_entries = os.path.join(self._cachedir, 'ENTRIES')


   @property
   def old_datapath(self):
      return self._old_datapath

   @property
   def new_datapath(self):
      return self._new_datapath

   @property
   def force(self):
      return self._force
   
   @property
   def stagingdir(self):
      return self._stagingdir
      
   @property
   def cachedir(self):
      return self._cachedir
   
   @property
   def cache_entries(self):
      return self._cache_entries
      
   '''
   get cache status: check where in the cache is the change stored
   '''
   def get_cached_paths(self):
      logger = logging.getLogger(__name__)

      if self.old_datapath == self.new_datapath:
         logger.error('Comparison paths are the same')
         sys.exit()

      is_subdir_oldpath = False
      is_subdir_newpath = False
      cached_old_path = self.old_datapath
      cached_new_path = self.new_datapath
    
      status = CacheStatus.NOT_CACHED
      logger.info('Checking cache status.')

      '''
      This is the caching logic where change information is saved and subsequently retrieved
      If no high-level diff exists for the data, then do a comparison
      - do the comparison for the all the indexed data
      - at runtime, decide if the comparison is between any subdirectories of the total diff
      '''
      if os.path.exists(self.cache_entries):
         logger.info('Cache exists... checking cache entries.')
         '''
         if the high-level diff exists,
         then check if it exists for the two data versions provided here
         '''
         with open(self.cache_entries, 'r') as f:
            cache = yaml.load(f)
            '''
            if changes for the newpath are in cache, then
            check if they are for the compared oldpath 
            '''
            if self.new_datapath in cache:
               '''
               if the diff paths are already compared, then get the corresponding directory;
               else, do the comparisons/diff
               '''
               if self.old_datapath in cache[self.new_datapath]:
                  '''
                  if both oldpath and newpath are in the cache
                  '''
                  logger.info('Changes are present in cache...')
                  status = CacheStatus.ALL_CACHED
               else:
                  '''
                  check if the oldpath is a subdirectory of a cached path change
                  '''
                  for o in cache[self.new_datapath]:
                     parent_path = o + os.sep
                     if self.old_datapath.startswith(parent_path):
                        logger.info('Changes can be derived from the cache.')
                        status = CacheStatus.OLD_PARENT_CACHED
                        cached_old_path = os.path.abspath(parent_path)
                        break
            else:
               '''
               if changes for the original newpath are not in cache,
               check if any parent directory changes are in cache
               '''
               d = os.path.dirname(self.new_datapath)
               '''
               check if any parent dir changes are calculated and cached
               '''
               while d != '/' and d not in cache:
                  d = os.path.dirname(d)
                  
               '''
               if changes for a matching parent are found,
               then check if oldpath changes are cached 
               '''
               if d != '/':
                  if self.old_datapath in cache[d]:
                     status = CacheStatus.NEW_PARENT_CACHED
                     cached_new_path = d
                  else:
                     for o in cache[d]:
                        parent_path = o + os.sep
                        if self.old_datapath.startswith(parent_path):
                           logger.info('Subdirectory changes can be derived from cache.')
                           status = CacheStatus.BOTH_PARENTS_CACHED
                           cached_old_path = os.path.abspath(parent_path)
                           cached_new_path = d
                           break

      return status, cached_old_path, cached_new_path


   '''
   find the high-level changes between two paths
   - if indexed and compared, then just fetch the comparison data
   - else scan and index all the data sets (files/directories) recursively
   '''
   def get_changes(self, cache_status, cached_old_path, cached_new_path):
      logger = logging.getLogger(__name__)

      is_subdir_oldpath = False
      is_subdir_newpath = False

      logger.info('Checking for changes between %s and %s', self.old_datapath, self.new_datapath)

      if cache_status == CacheStatus.NOT_CACHED:
         change_dir = comparator.compare(self.old_datapath, self.new_datapath, self.stagingdir)
      else:
         with open(self.cache_entries, 'r') as f:
            cache = yaml.load(f)
            change_dir = cache[cached_new_path][cached_old_path]

      if cached_old_path != self.old_datapath:
         is_subdir_oldpath = True
         
      if cached_new_path != self.new_datapath:
         is_subdir_newpath = True
         
      logger.info('Retrieving changes between %s and %s', self.old_datapath, self.new_datapath)
      
      change = FilesystemChange(cached_old_path, cached_new_path, self.stagingdir)

      if is_subdir_newpath:
         indexdir = os.path.join(self.stagingdir, 'indexes', get_hash_id(cached_new_path))
         subdir_nfiles = get_subdir_nfiles(self.new_datapath, indexdir)
         change.new_nfiles = subdir_nfiles

      if is_subdir_oldpath:
         indexdir = os.path.join(self.stagingdir, 'indexes', get_hash_id(cached_old_path))
         subdir_nfiles = get_subdir_nfiles(self.old_datapath, indexdir)
         change.old_nfiles = subdir_nfiles

      change_data_dir = os.path.join(self.cachedir, change_dir)
      if not (is_subdir_oldpath or is_subdir_newpath):
         set_change_from_cache(change, change_data_dir)
      else:
         compare_hash = dacman_utils.hash_comparison_id(self.old_datapath, self.new_datapath)
         change_data_subdir = os.path.join(self.cachedir, compare_hash)
         if os.path.exists(change_data_subdir):
            set_change_from_cache(change, change_data_subdir)
         else:
            save_subdir_changes_to_cache(change, self.stagingdir,
                                         cached_old_path, cached_new_path,
                                         self.old_datapath, self.new_datapath,
                                         is_subdir_oldpath, is_subdir_newpath,
                                         change_data_dir, change_data_subdir)

            logger.info('Updating change cache entries')
            change_id = dacman_utils.hash_comparison_id(self.old_datapath, self.new_datapath)
            change_info = {self.new_datapath : {self.old_datapath: change_id}}
            dacman_utils.update_yaml(change_info, self.cache_entries)

      logger.info('Change retrieval completed')

      return change

######################################################################################

'''
find the high-level changes between two paths
- if indexed and compared, then just fetch the comparison data
- else scan and index all the data sets (files/directories) recursively
'''
## deprecated
def changes(old_datapath, new_datapath, force=False, custom_stagingdir=None):
    logger = logging.getLogger(__name__)

    #old_datapath = os.path.abspath(old_path)
    #new_datapath = os.path.abspath(new_path)

    if old_datapath == new_datapath:
       logger.error('Comparison paths are the same')
       sys.exit()

    if not custom_stagingdir:
       stagingdir = dacman_utils.DACMAN_STAGING_LOC
    else:
       stagingdir = custom_stagingdir

    is_subdir_oldpath = False
    is_subdir_newpath = False
    cached_old_path = old_datapath
    cached_new_path = new_datapath

    cachedir = os.path.join(stagingdir, 'cache')
    cache_entries = os.path.join(cachedir, 'ENTRIES')

    logger.info('Checking for changes between %s and %s', old_datapath, new_datapath)

    '''
    This is the caching logic where change information is saved and subsequently retrieved
    If no high-level diff exists for the data, then do a comparison
    - do the comparison for the all the indexed data
    - at runtime, decide if the comparison is between any subdirectories of the total diff
    '''
    if not os.path.exists(cache_entries) or force:
        logger.info('Cache is empty... starting dataset comparison')
        change_dir = comparator.compare(old_datapath, new_datapath, stagingdir)
    else:
        logger.info('Checking for pre-calculated and cached changes.')
        '''
        if the high-level diff exists, then check if it exists for the two data versions provided here
        '''
        with open(cache_entries, 'r') as f:
            cache = yaml.load(f)
            '''
            if changes for the newpath are in cache, then
            check if they are for the compared oldpath 
            '''
            if new_datapath in cache:
               '''
               if the diff paths are already compared, then get the corresponding directory;
               else, do the comparisons/diff
               '''
               if old_datapath in cache[new_datapath]:
                  '''
                  if both oldpath and newpath are in the cache
                  '''
                  logger.info('Changes are present in cache... fetching change information.')
                  change_dir = cache[new_datapath][old_datapath]
               else:
                  '''
                  check if the oldpath is a subdirectory of a cached path change
                  '''
                  for o in cache[new_datapath]:
                     parent_path = o + os.sep
                     if old_datapath.startswith(parent_path):
                        logger.info('Changes can be derived from the cache.')
                        change_dir = cache[new_datapath][o]
                        cached_old_path = os.path.abspath(parent_path)
                        break
                     '''
                     if the oldpath is neither in cache nor is a subdir of a cache entry,
                     then it's a new comparison
                     '''
                  else:
                     logger.info('Changes are not cached... initiating dataset comparison.')
                     change_dir = comparator.compare(old_datapath, new_datapath, stagingdir)
            else:
               '''
               if changes for the original newpath are not in cache,
               check if any parent directory changes are in cache
               '''
               d = os.path.dirname(new_datapath)
               '''
               check if any parent dir changes are calculated and cached
               '''
               while d != '/' and d not in cache:
                  d = os.path.dirname(d)
                  
               '''
               if changes for a matching parent are found,
               then check if oldpath changes are cached 
               '''
               if d != '/':
                  if old_datapath in cache[d]:
                     change_dir = cache[d][old_datapath]
                     cached_new_path = d
                  else:
                     for o in cache[d]:
                        parent_path = o + os.sep
                        if old_datapath.startswith(parent_path):
                           logger.info('Subdirectory changes can be derived from cache.')
                           change_dir = cache[d][o]
                           cached_old_path = os.path.abspath(parent_path)
                           cached_new_path = d
                           break
                     else:
                        logger.info('Changes are not pre-calculated... initiating dataset comparison.')
                        change_dir = comparator.compare(old_datapath, new_datapath, stagingdir)
               else:
                  '''
                  if changes are not present in the cache, then compare
                  '''
                  logger.info('Changes are not pre-calculated... initiating dataset comparison.')
                  change_dir = comparator.compare(old_datapath, new_datapath, stagingdir)

    if cached_old_path != old_datapath:
       is_subdir_oldpath = True

    if cached_new_path != new_datapath:
       is_subdir_newpath = True

    logger.info('Retrieving changes between %s and %s', old_datapath, new_datapath)

    #change = FilesystemChange(old_datapath, new_datapath, stagingdir)
    change = FilesystemChange(cached_old_path, cached_new_path, stagingdir)

    if is_subdir_newpath:
       indexdir = os.path.join(stagingdir, 'indexes', get_hash_id(cached_new_path))
       subdir_nfiles = get_subdir_nfiles(new_datapath, indexdir)
       change.new_nfiles = subdir_nfiles

    if is_subdir_oldpath:
       indexdir = os.path.join(stagingdir, 'indexes', get_hash_id(cached_old_path))
       subdir_nfiles = get_subdir_nfiles(old_datapath, indexdir)
       change.old_nfiles = subdir_nfiles

    change_data_dir = os.path.join(cachedir, change_dir)
    #print(change_data_dir)
    if not (is_subdir_oldpath or is_subdir_newpath):
       set_change_from_cache(change, change_data_dir)
    else:
       compare_hash = dacman_utils.hash_comparison_id(old_datapath, new_datapath)
       change_data_subdir = os.path.join(cachedir, compare_hash)
       if os.path.exists(change_data_subdir):
          set_change_from_cache(change, change_data_subdir)
       else:
          save_subdir_changes_to_cache(change, stagingdir,
                                       cached_old_path, cached_new_path,
                                       old_datapath, new_datapath,
                                       is_subdir_oldpath, is_subdir_newpath,
                                       change_data_dir, change_data_subdir)

          logger.info('Updating change cache entries')
          change_id = dacman_utils.hash_comparison_id(old_datapath, new_datapath)
          change_file = os.path.join(cachedir, 'ENTRIES')
          change_info = {new_datapath : {old_datapath: change_id}}
          dacman_utils.update_yaml(change_info, change_file)

    logger.info('Change retrieval completed')

    return change


def get_subdir_nfiles(datapath, indexdir):
   paths_file = os.path.join(indexdir, 'FILEPATHS')
   datapath_file = os.path.join(indexdir, 'DATAPATH')
   parent_path = ''
   with open(datapath_file) as f:
      parent_path = f.readline().strip()

   nfiles = 0
   with open(paths_file) as f:
      for path in f:
         abspath = os.path.join(parent_path, path)
         if abspath.startswith(datapath):
            nfiles += 1

   return nfiles


'''
if change is already calculated, just retrieve it
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

   metainfo = dacman_utils.load_yaml(os.path.join(change_dir, 'META_INFO'))
   change.old_nfiles = metainfo['base']['nfiles']
   change.new_nfiles = metainfo['revision']['nfiles']
   

def display(change):
    print("Additions: {}, Deletions: {}, Modifications: {}, Metadata changes: {}, Unchanged: {}".
          format(len(change.added),
                 len(change.deleted),
                 len(change.modified),
                 len(change.metachange),
                 len(change.unchanged)))


'''
derives subdirectory-level changes from cached parent directory changes
'''
def save_subdir_changes_to_cache(change, stagingdir,
                                 cached_old_path, cached_new_path,
                                 old_datapath, new_datapath,
                                 is_subdir_oldpath, is_subdir_newpath,
                                 change_dir, change_subdir):
   change_data = {'ADDED': [], 'DELETED': [],
                  'MODIFIED': {}, 'METACHANGE': {},
                  'UNCHANGED': []}

   if is_subdir_oldpath and not is_subdir_newpath:
      '''
      if oldpath is a subdir of an indexed path, then mark all the files that are
      not in oldpath as added w.r.t the newpath
      '''
      for change_type in change_data:
         base_change_file = os.path.join(change_dir, change_type)
         if change_type == 'ADDED':
            with open(base_change_file) as f:
               lines = f.readlines()
               change_data[change_type] = [line.strip() for line in lines]
         elif change_type == 'DELETED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(cached_old_path, line.strip())
                  if path.startswith(old_datapath):
                     rel_subpath = os.path.relpath(path, old_datapath)               
                     change_data[change_type].append(rel_subpath)
               lines = f.readlines()
               change_data[change_type] = [line.strip() for line in lines]
         elif change_type == 'UNCHANGED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(cached_old_path, line.strip())
                  if path.startswith(old_datapath):
                     '''
                     there's nothing unchanged anymore, everything is metachange
                     because the directory depths have changed and so have the relative
                     file paths
                     '''
                     rel_subpath = os.path.relpath(path, old_datapath)               
                     change_data['METACHANGE'][line.strip()] = rel_subpath
                  else:
                     change_data['ADDED'].append(line.strip())
         elif change_type == 'METACHANGE':
            with open(base_change_file) as f:
               for line in f:
                  kv = line.split(':')
                  path = os.path.join(cached_old_path, kv[1].strip())
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
                  path = os.path.join(cached_old_path, kv[1].strip())
                  if path.startswith(old_datapath):
                     rel_subpath = os.path.relpath(path, old_datapath)
                     change_data[change_type][kv[0]] = rel_subpath
                  else:
                     change_data['ADDED'].append(kv[0])
   elif not is_subdir_oldpath and is_subdir_newpath:
      '''
      if newpath is a subdir of an indexed path, then mark all the files that are
      not in newpath as deleted
      '''
      for change_type in change_data:
         base_change_file = os.path.join(change_dir, change_type)
         if change_type == 'ADDED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(cached_new_path, line.strip())
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
                  path = os.path.join(cached_new_path, orig_path)
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
                  path = os.path.join(cached_new_path, kv[0])
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
                  path = os.path.join(cached_new_path, kv[0])
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
                  path = os.path.join(cached_new_path, line.strip())
                  if path.startswith(new_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)
                     change_data[change_type].append(rel_subpath)
         elif change_type == 'DELETED':
            with open(base_change_file) as f:
               for line in f:
                  path = os.path.join(cached_old_path, line.strip())
                  if path.startswith(old_datapath):
                     rel_subpath = os.path.relpath(path, new_datapath)
                     change_data[change_type].append(rel_subpath)
         elif change_type == 'UNCHANGED':
            with open(base_change_file) as f:
               for line in f:
                  orig_path = line.strip()
                  path = os.path.join(cached_new_path, orig_path)
                  old_path = os.path.join(cached_old_path, orig_path)
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
                  path = os.path.join(cached_new_path, orig_new_path)
                  old_path = os.path.join(cached_old_path, orig_old_path)
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
                  path = os.path.join(cached_new_path, orig_new_path)
                  old_path = os.path.join(cached_old_path, orig_old_path)
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

   _meta_info = {'base': {'dataset_id': old_datapath,
                          'nfiles': change.old_nfiles},
                 'revision': {'dataset_id': new_datapath,
                              'nfiles': change.new_nfiles}}
   _metafile = os.path.join(change_subdir, 'META_INFO')
   dacman_utils.dump_yaml(_meta_info, _metafile)

   change.add_changes(change_data['ADDED'], change_data['DELETED'],
                      change_data['MODIFIED'], change_data['UNCHANGED'],
                      change_data['METACHANGE'])
   change.calculate_degree()

        
def main(args):
    oldpath = os.path.abspath(args.oldpath)
    newpath = os.path.abspath(args.newpath)
    stagingdir = args.stagingdir
    force = args.force

    #change = changes(oldpath, newpath, force, stagingdir)
    changeManager = ChangeManager(oldpath, newpath, force, stagingdir)
    status, cached_old_path, cached_new_path = changeManager.get_cached_paths()
    change = changeManager.get_changes(status, cached_old_path, cached_new_path)
    display(change)

def s_main(args):
    oldpath = args['oldpath']
    newpath = args['newpath']
    stagingdir = args['stagingdir']

    change = changes(oldpath, newpath, stagingdir)
    display(change)

if __name__ == '__main__':
   args = {'oldpath': sys.argv[1], 'newpath': sys.argv[2]}

   s_main(args)
