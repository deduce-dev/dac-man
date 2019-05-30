"""
`dacman.__init__`
====================================

.. currentmodule:: dacman.__init__

:platform: Unix, Mac
:synopsis: Package initialization

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

from dacman.core.scanner import scan
from dacman.core.indexer import index
from dacman.core.change import changes, Change, FilesystemChange
from dacman.core.diff import Differ
from dacman.core.persistence import DirectoryTree, DiffStore

import logging
import logging.config
import os
import yaml
import sys

from ._version import __version__


def setup_logging(log_config, log_level):
    if os.path.exists(log_config):
        with open(log_config, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(stream=sys.stdout, level=log_level)


def init_log():
    #log_file = resource_filename(Requirement.parse("dacman"),"config/logging.yaml")
    log_file = os.path.join(os.getenv('HOME'), '.dacman/config/logging.yaml')
    #log_config = 'config/logging.yaml'
    log_config = log_file
    log_level = logging.INFO
    setup_logging(log_config, log_level)


init_log()


'''
Only exposing the diff related classes for the API.
The scan, index and change functions remain only
part of the command-line utility.
'''
#__all__ = ['scan', 'index', 'changes', 'Change', 'Differ', 'DirectoryTree', 'DiffStore']
__all__ = ['Change', 'FilesystemChange', 'Differ', 'DirectoryTree', 'DiffStore',
           'scan', 'index', 'changes']

