"""
`dacman.compare.data`
====================================

.. currentmodule:: dacman.compare.data

:platform: Unix, Mac
:synopsis: Module finding `diff` between two datasets and can take optional args.

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk

import os
import logging
import subprocess
import sys

from dacman.compare.plugin import PluginManager
from dacman.compare.base import Comparator


__modulename__ = 'data'
logger = logging.getLogger(__name__)


def diff(new_file, old_file, *argv, comparator_plugin=None):
    external_plugin = False
    comparator = None
    if comparator_plugin is None:
        filename_1, file_extension_1 = os.path.splitext(new_file)
        filename_2, file_extension_2 = os.path.splitext(old_file)
        file_extension_1 = file_extension_1[1:]
        file_extension_2 = file_extension_2[1:]
        if file_extension_1 != file_extension_2:
            comparator = PluginManager.load_comparator('default')
        else:
            comparator = PluginManager.load_comparator(file_extension_1)
    else:
        if isinstance(comparator_plugin, str):
            external_plugin = True
        elif issubclass(comparator_plugin, Comparator):
            comparator = comparator_plugin()
        else:
            print("Invalid comparator plugin")
            logger.error('Invalid comparator plugin: {}'.format(comparator_plugin))
            sys.exit()

    if external_plugin:
        print("External comparator plugin = {}".format(comparator_plugin))
        logger.info('Comparing {} and {} using {}'.format(new_file,
                                                          old_file,
                                                          comparator_plugin))
        result = _external(comparator_plugin, new_file, old_file, *argv)
    else:
        print("Data comparator plugin = {}".format(comparator.__class__.__name__))

        logger.info('Comparing {} and {} using {}'.format(new_file,
                                                          old_file,
                                                          comparator.__class__.__name__))

        changes = comparator.compare(new_file, old_file, *argv)
        result = comparator.stats(changes)
    if result is not None:
        print(result)


def _external(plugin, new_file, old_file, *argv):
    try:
        proc = subprocess.Popen([plugin, new_file, old_file, *argv],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=_get_env_with_added_to_PATH('./'),
                            # universal_newlines forces the output of communicate()
                            # to be returned as strings instead of bytes
                            universal_newlines=True
                            )
    except FileNotFoundError as e:
        logger.error('Plugin definition not found (please ensure that the path is correct and the script is executable).')
        logger.error(e)
        return None
    out, err = proc.communicate()
    if err:
        logger.error('Error analyzing changes:\n%s', err)
        return None
    else:
        logger.info('Change calculation completed')
        return out


def _get_updated_env(updates):
    env = dict(os.environ)
    env.update(updates)
    return env


def _get_env_with_added_to_PATH(dir_):
    old_path = os.environ['PATH']
    new_path = dir_ + ':' + old_path
    return _get_updated_env({'PATH': new_path})
