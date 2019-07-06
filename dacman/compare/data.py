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

from dacman.compare.plugin import PluginManager


__modulename__ = 'data'
logger = logging.getLogger(__name__)


def diff(new_file, old_file, *argv, comparator_plugin=None):
    if comparator_plugin is None:
        filename_1, file_extension_1 = os.path.splitext(new_file)
        filename_2, file_extension_2 = os.path.splitext(old_file)
        if file_extension_1 != file_extension_2:
            comparator = PluginManager.load_comparator('default')
        else:
            comparator = PluginManager.load_comparator(file_extension_1)
    else:
        comparator = comparator_plugin

    print('Comparing {} and {} using {}'.format(new_file,
                                                old_file,
                                                comparator.__class__.__name__))

    logger.info('Comparing {} and {} using {}'.format(new_file,
                                                      old_file,
                                                      comparator.__class__.__name__))

    changes = comparator.compare(new_file, old_file, *argv)
    result = comparator.stats(changes)
    if result is not None:
        print(result)


# def simple_diff(new_file, old_file, *argv):
#     filename_1, file_extension_1 = os.path.splitext(new_file)
#     filename_2, file_extension_2 = os.path.splitext(old_file)
#     print(file_extension_1, file_extension_2)
#     if file_extension_1 != file_extension_2:
#         comparator = PluginManager.load_comparator('default')
#     else:
#         comparator = PluginManager.load_comparator(file_extension_1)
#
#     print(comparator)
#
#     print('Comparing {} and {} using comparator {}'.format(new_file,
#                                                            old_file,
#                                                            comparator))
#
#     #logger.info('Comparing {} and {} using comparator {}'.format(new_file,
#     #                                                             old_file,
#     #                                                             comparator.__name__))
#
#     result = comparator.compare(new_file, old_file, *argv)
#     print(result)


