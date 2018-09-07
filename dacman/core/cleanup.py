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
   logger.info('Removing staging data for %s', ', '.join(datadirs))
   for datadir in datadirs:
      path = os.path.abspath(datadir)
      deducedir = os.path.join(dacman_utils.DACMAN_STAGING_LOC, get_hash_id(path))
      if os.path.exists(deducedir):
         shutil.rmtree(deducedir)
         #print("Indexes removed for data directory: {}".format(datadir))
         logger.info('Staging data removed for %s', datadir)
      elif os.path.exists(datadir):
         logger.warn('Indexes and metadata for directory %s are not staged', datadir)
      else:
         #print("Data directory {} is not indexed".format(datadir))
         logger.error('Data directory %s does not exist', datadir)

def main(args):
   datadirs = args.datadirs
   clean(datadirs)
