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
from pathlib import Path
import pkg_resources

from ._version import __version__


_PATH_USER_DIR = Path.home() / '.dacman'


def _setup_user_dir(resource_names=None):
    """
    - If the directory doesn't exist, it will create it
    - Config files, if missing, will be copied over from package resources.

    Files are expressed in terms of pkg_resources resource names, relative to this module.
    """
    basepath = _PATH_USER_DIR
    basepath.mkdir(exist_ok=True, parents=True)

    resource_names = resource_names or ['config/logging.yaml', 'config/plugins.yaml']

    for res_name in resource_names:
        filepath = basepath / res_name
        # TODO not clear if there's a way to use logging for these
        # since we're setting up the log configuration here
        # print(f'res_name={res_name}')
        # print(f'filepath={filepath}')
        # print(f'basepath={basepath}')
        if not filepath.exists():
            # print(f'filepath.exists()={filepath.exists()}')
            filepath.parent.mkdir(exist_ok=True, parents=True)
            # TODO add try/except here if resource is not found
            content = pkg_resources.resource_string('dacman', res_name)
            # print(f'type(content)={type(content)}')
            filepath.write_bytes(content)


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


_setup_user_dir()
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

