"""
`dacman.core.add_metadata`
====================================

.. currentmodule:: dacman.core.metadata

:platform: Unix, Mac
:synopsis: Module to add user-defined metadata to the datasets

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
from dacman.core.utils import cprint, get_hash_id
import dacman.core.utils as dacman_utils
import logging

__modulename__ = 'metadata'


def insert(datapath, usermeta, custom_stagingdir=None):
   logger = logging.getLogger(__name__)

   if not custom_stagingdir:
      stagingdir = dacman_utils.DACMAN_STAGING_LOC
   else:
      stagingdir = custom_stagingdir

   indexdir = os.path.join(stagingdir, 'indexes', get_hash_id(datapath))

   if not os.path.exists(indexdir):
      logger.error('Data is not indexed... please index before adding metadata!')
      sys.exit()

   if not usermeta:
      logger.warn('No user metadata provided. Exiting...')
      return

   meta_file = os.path.join(indexdir, 'METADATA')

   metadata = dacman_utils.load_yaml(meta_file)
   if not metadata:
         metadata = {}
   metadata['USER_DEFINED_METADATA'] = usermeta
   dacman_utils.dump_yaml(metadata, meta_file)   
      
   logger.info('User metadata added')


def retrieve(datapath, custom_stagingdir=None):
   logger = logging.getLogger(__name__)

   if not custom_stagingdir:
      stagingdir = dacman_utils.DACMAN_STAGING_LOC
   else:
      stagingdir = custom_stagingdir

   indexdir = os.path.join(stagingdir, 'indexes', get_hash_id(datapath))

   if not os.path.exists(indexdir):
      logger.error('Data is not indexed... please index before retrieving metadata!')
      sys.exit()

   meta_file = os.path.join(indexdir, 'METADATA')

   metadata = {}
   metadata = dacman_utils.load_yaml(meta_file)   
   if not metadata:
      metadata = {}
   elif 'USER_DEFINED_METADATA' in metadata:
      usermeta = metadata['USER_DEFINED_METADATA']
      print(usermeta)
   else:
      print('No user-defined metadata available for the dataset')
      
   logger.info('User metadata retrieved')
   

def append(datapath, usermeta, custom_stagingdir=None):
   logger = logging.getLogger(__name__)

   if not custom_stagingdir:
      stagingdir = dacman_utils.DACMAN_STAGING_LOC
   else:
      stagingdir = custom_stagingdir

   indexdir = os.path.join(stagingdir, 'indexes', get_hash_id(datapath))

   if not os.path.exists(indexdir):
      logger.error('Data is not indexed... please index before adding metadata!')
      sys.exit()

   if not usermeta:
      logger.warn('No user metadata provided. Exiting...')
      return

   meta_file = os.path.join(indexdir, 'METADATA')

   metadata = dacman_utils.load_yaml(meta_file)
   if not metadata:
         metadata = {}
   newmeta = ''
   if 'USER_DEFINED_METADATA' in metadata:
      newmeta = metadata['USER_DEFINED_METADATA']

   newmeta += ', ' + usermeta
   extended_metadata = {'USER_DEFINED_METADATA': newmeta}
   dacman_utils.dump_yaml(extended_metadata, meta_file)   
      
   logger.info('New user metadata added')
    
def main(args):
   datapath = os.path.abspath(args.datapath)
   stagingdir = args.stagingdir
   usermeta = args.metadata
   func_map = {'insert': insert, 'retrieve': retrieve, 'append': append}
   func = func_map[args.option]
   if args.option == 'retrieve':
      func(datapath, stagingdir)
   else:
      func(datapath, usermeta, stagingdir)

def s_main(args):
   datapath = args['datapath']
   stagingdir = None
   if 'stagingdir' in args:
      stagingdir = args['stagingdir']

   scan(datapath, stagingdir)

if __name__ == '__main__':
   args = {'datapath': sys.argv[1]}

   s_main(args)
