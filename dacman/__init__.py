"""
`dacman.__init__`
====================================

.. currentmodule:: dacman.__init__

:platform: Unix, Mac
:synopsis: Package initialization

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

from dacman.compare.data import diff
from dacman.compare.manager import DataDiffer
from dacman.runtime import Executor
from dacman import plugins

import logging
import logging.config
import os
import yaml
import sys

from ._version import __version__


def _setup_logging(log_config, log_level):
    if os.path.exists(log_config):
        with open(log_config, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(stream=sys.stdout, level=log_level)


def _init_log():
    #log_file = resource_filename(Requirement.parse("dacman"),"config/logging.yaml")
    log_file = os.path.join(os.getenv('HOME'), '.dacman/config/logging.yaml')
    #log_config = 'config/logging.yaml'
    log_config = log_file
    log_level = logging.INFO
    _setup_logging(log_config, log_level)


_init_log()


'''
Only exposing the diff related classes for the API.
The scan, index and change functions remain only
part of the command-line utility.
'''
__all__ = ['diff', 'DataDiffer', 'Executor', 'plugins']

#__all__ = ['scan', 'index', 'changes', 'Change', 'Differ', 'DirectoryTree', 'DiffStore']
#__all__ = ['Change', 'FilesystemChange', 'Differ', 'DirectoryTree', 'DiffStore',
#           'scan', 'index', 'changes']

