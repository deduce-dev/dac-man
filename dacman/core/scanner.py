"""
`dacman.core.scanner`
====================================

.. currentmodule:: dacman.core.scanner

:platform: Unix, Mac
:synopsis: Module that scans and captures filesystem metadata

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

try:
   from os import scandir, walk
except ImportError:
   from scandir import scandir, walk

import yaml
import os
import sys
import pwd
import grp
import fnmatch
#from datetime import datetime
from dacman.core.persistence import DirectoryTree
from dacman.core.utils import cprint, get_hash_id
import dacman.core.utils as dacman_utils
import logging

__modulename__ = 'scanner'

"""
recursively scans a directory                                                                     
sub-directories are not returned, only the files inside the subdirectories are returned           
"""
def scantree(path, excludes, follow_symlinks):
   for entry in scandir(path):
      if entry.is_dir(follow_symlinks=follow_symlinks) and entry.name not in excludes:
         yield entry
         for subentry in scantree(entry.path, excludes, follow_symlinks):
            yield subentry
      elif entry.name not in excludes:
         yield entry

def scan_only_dir(path, excludes, follow_symlinks):
   for entry in scandir(path):
         yield entry


def get_metadata(entry):
   file_stats = entry.stat()
   owner = pwd.getpwuid(file_stats.st_uid).pw_name
   group = grp.getgrgid(file_stats.st_gid).gr_name
   size = file_stats.st_size
   metadata = {'owner': owner, 'group': group, 'size': size}
   '''
   if entry.is_dir(follow_symlinks=False):
      metadata['type'] = 'dir'
   else:
      metadata['type'] = 'file'
   '''
   return metadata


'''
scans a data directory
'''
def scan(datapath, custom_stagingdir=None, nonrecursive=False, symlinks=False, details=False, ignorelist=[]):
   logger = logging.getLogger(__name__)

   if not os.path.exists(datapath):
      #cprint(__modulename__, 'Datapath `{}` does not exist!'.format(datapath))
      logger.error('Datapath %s does not exist!', datapath)
      sys.exit()
   
   if not os.path.isdir(datapath):
      #print('Indexing currently allowed only for data in a directory.')
      #cprint(__modulename__, 'Indexing currently allowed only for data in a directory.')
      logger.error('Indexing currently allowed only for data in a directory.')
      sys.exit()
      
   if not custom_stagingdir:
      stagingdir = dacman_utils.DACMAN_STAGING_LOC
   else:
      stagingdir = custom_stagingdir

   indexdir = os.path.join(stagingdir, 'indexes', get_hash_id(datapath))

   if not os.path.exists(indexdir):
      os.makedirs(indexdir)

   entries = []
   follow_symlinks = symlinks
   excluded_dirs = {'.dacman': True}
   metainfo = {}

   # keeping this for feature enhancements and future optimizations
   #dirtree = DirectoryTree(datapath, stagingdir)
   #cprint(__modulename__, 'Scanning datapath {}'.format(datapath))
   logger.info('Scanning datapath %s', datapath)

   ### Doing this is too slow ###
   """
   for entry in scantree(datapath, excluded_dirs, follow_symlinks):
      filepath = entry.path
      relative_path = os.path.relpath(filepath, datapath)
      '''
      ### Doing this is too slow ###
      # saving only info about the files and not directories
      if not entry.is_dir(follow_symlinks=False):
         metainfo[relative_path] = get_metadata(entry)
      '''
      # keeping this for feature enhancements and future optimizations
      #dirtree.add(entry.path)

   #dirtree.save()
   #dirtree.close()

   '''
   meta_path = os.path.join(stagingdir, 'METADATA')    
   cprint(__modulename__, 'Dumping metadata')
   dump(metainfo, meta_path)
   '''
   """
   scan_funcs = {False: scantree, True: scan_only_dir}
   scan_fn = scan_funcs[nonrecursive]

   paths_file = os.path.join(indexdir, 'FILEPATHS')    
   meta_file = os.path.join(indexdir, 'METADATA')
   # open the metadata file
   mf = open(meta_file, 'w')

   if nonrecursive:
      logger.info('Ignoring subdirectory scans: scanning files only in the present directory')

   '''
   if there is no file to ignore
   '''
   if len(ignorelist) == 0:
      with open(paths_file, 'w') as f:
         for entry in scan_fn(datapath, excluded_dirs, follow_symlinks):
            filepath = entry.path
            relative_path = os.path.relpath(filepath, datapath)
            '''
            only save the file paths and not dir paths
            '''
            if not entry.is_dir(follow_symlinks=symlinks):
               line = '{}\n'.format(relative_path)
               f.write(line)
               if details:
                  file_stats = entry.stat()
                  owner = pwd.getpwuid(file_stats.st_uid).pw_name
                  group = grp.getgrgid(file_stats.st_gid).gr_name
                  size = file_stats.st_size
                  #mtime = datetime.fromtimestamp(file_stats.st_mtime).strftime("%d %B %Y %I:%M:%S")
                  # File modification time doesn't make sense here, because we compare two versions
                  #mtime = file_stats.st_mtime
                  metadata = relative_path+':owner='+owner+',group='+group+ ',size='+str(size)+'\n'
                  #metadata = relative_path+':owner='+owner+',group='+group+\
                  #    ',size='+str(size)+',mtime='+str(mtime)+'\n'
                  mf.write(metadata)
   else:
      with open(paths_file, 'w') as f:
         for entry in scan_fn(datapath, excluded_dirs, follow_symlinks):
            filepath = entry.path
            relative_path = os.path.relpath(filepath, datapath)
            ignore_file = False
            for ignore_pattern in ignorelist:
               if fnmatch.fnmatch(relative_path, ignore_pattern):
                  ignore_file = True
                  break
            '''
            only save the file paths and not dir paths
            '''
            if not (ignore_file or entry.is_dir(follow_symlinks=symlinks)):
               line = '{}\n'.format(relative_path)
               f.write(line)
               if details:
                  file_stats = entry.stat()
                  owner = pwd.getpwuid(file_stats.st_uid).pw_name
                  group = grp.getgrgid(file_stats.st_gid).gr_name
                  size = file_stats.st_size
                  #mtime = datetime.fromtimestamp(file_stats.st_mtime).strftime("%d %B %Y %I:%M:%S")
                  #mtime = file_stats.st_mtime
                  metadata = relative_path+':owner='+owner+',group='+group+ ',size='+str(size)+'\n'
                  #metadata = relative_path+':owner='+owner+',group='+group+\
                  #    ',size='+str(size)+',mtime='+str(mtime)+'\n'
                  mf.write(metadata)

   logger.info('Saving path metadata and directory scan information')

   basepath_file = os.path.join(indexdir, 'DATAPATH')
   with open(basepath_file, 'w') as f:
      f.write('{}\n'.format(datapath))

   # close the metadata file
   mf.close()

   #cprint(__modulename__, 'Scan complete')
   logger.info('Directory scan complete')

   return indexdir

def dump(metainfo, meta_path):
   with open(meta_path, 'w') as f:
      yaml.dump(metainfo, f, default_flow_style=False)
    
    
def main(args):
   datapath = os.path.abspath(args.datapath)
   stagingdir = args.stagingdir
   nonrecursive = args.nonrecursive
   symlinks = args.symlinks
   details = args.metadetails
   if args.ignore is None:
      ignorelist = []
   else:
      ignorelist = args.ignore   
   scan(datapath, stagingdir, nonrecursive, symlinks, details, ignorelist)

def s_main(args):
   datapath = args['datapath']
   stagingdir = None
   if 'stagingdir' in args:
      stagingdir = args['stagingdir']

   scan(datapath, stagingdir)

if __name__ == '__main__':
   args = {'datapath': sys.argv[1]}

   s_main(args)
