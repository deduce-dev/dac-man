"""
`dacman.core.cleanup`
====================================

.. currentmodule:: dacman.core.cleanup

:platform: Unix, Mac
:synopsis: Module to cleanup Dac-Man indexes and metadata

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

import os
import sys
import shutil
import logging
from dacman.core.utils import get_hash_id
import dacman.core.utils as dacman_utils

def clean(datadirs):
   logger = logging.getLogger(__name__)
   logger.info('Removing indexes for %s', ', '.join(datadirs))
   indexdir = os.path.join(dacman_utils.DACMAN_STAGING_LOC, 'indexes')
   cachedir = os.path.join(dacman_utils.DACMAN_STAGING_LOC, 'cache')
   cachefile = os.path.join(cachedir, 'ENTRIES')
   if os.path.exists(cachefile):
      cache = dacman_utils.load_yaml(cachefile)
      for datadir in datadirs:
         path = os.path.abspath(datadir)
         if path in cache:
            for comp in cache[path]:
               cache_data = os.path.join(cachedir, cache[path][comp])
               shutil.rmtree(cache_data)
            del cache[path]
         else:
            to_delete = []
            for k in cache:
               for s in cache[k]:
                  if s == path:
                     to_delete.append([k, s])
            for elem in to_delete:
               k, s = elem[0], elem[1]
               cache_data = os.path.join(cachedir, cache[k][s])
               shutil.rmtree(cache_data)               
               del cache[k][s]
      dacman_utils.dump_yaml(cache, cachefile)

   for datadir in datadirs:
      path = os.path.abspath(datadir)
      indexes = os.path.join(indexdir, get_hash_id(path))
      if os.path.exists(indexes):
         index_file = os.path.join(indexdir, 'INDEXED_PATHS')
         shutil.rmtree(indexes)
         index_metadata = dacman_utils.load_yaml(index_file)
         del index_metadata[path]
         dacman_utils.dump_yaml(index_metadata, index_file)
         logger.info('Indexes removed for %s', datadir)
      elif os.path.exists(datadir):
         logger.warn('Indexes and metadata for directory %s are not staged', datadir)
      else:
         logger.error('Data directory %s does not exist', datadir)


def main(args):
   datadirs = args.datadirs
   clean(datadirs)
