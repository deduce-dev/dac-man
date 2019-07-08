"""
`dacman.core.diff`
====================================

.. currentmodule:: dacman.core.diff

:platform: Unix, Mac
:synopsis: Module finding `diff` between two datasets

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk

import sys
import os
import difflib

from dacman.core.change import ChangeManager
import dacman.core.change as change
from dacman.core.utils import get_hash_id
import dacman.core.utils as dacman_utils
from dacman.compare.manager import DataDiffer
from dacman.runtime import Executor

import logging

try:
    from mpi4py import MPI
    MPI4PY_IMPORT = True
except ImportError:
    MPI4PY_IMPORT = False

__modulename__ = 'diff'


class Differ(object):
    def __init__(self, diff_all=False, custom_analyzer=None, executor=Executor.DEFAULT, outdir=None):
        self.old_path = None
        self.new_path = None
        self.stagingdir = dacman_utils.DACMAN_STAGING_LOC
        self._diff_all = diff_all
        self.custom_analyzer = custom_analyzer
        self.diffdir = None
        self.diff_pairs = []
        self.executor = executor
        self.outdir = outdir
        self.save_changes = False

        self.old_path_is_file = False
        self.new_path_is_file = False

        if outdir is not None:
            self.save_changes = True
        self.logger = logging.getLogger(__name__)

    def set_paths(self, old_path, new_path, custom_stagingdir=None):
        self.old_path = os.path.abspath(old_path)
        self.new_path = os.path.abspath(new_path)
        self.old_path_is_file = os.path.isfile(self.old_path)
        self.new_path_is_file = os.path.isfile(self.new_path)
        if custom_stagingdir:
            self.stagingdir = custom_stagingdir

    '''
    calculating longest common substring between two paths to avoid relative path queries
    '''
    def common_path(self, total_path, actual_path):
        match = difflib.SequenceMatcher(None, actual_path, total_path).find_longest_match(0, len(actual_path), 0,
                                                                                          len(total_path))
        matched_path = actual_path[match.a: match.a + match.size]
        return matched_path

    '''
    get the file pairs that have changed
    '''
    def get_change_pairs(self):
        if not (self.old_path and self.new_path):
            self.logger.error('Old and new datapaths are not specified!')
            sys.exit()

        change_pairs = []

        old_base = self.old_path
        new_base = self.new_path
        self.logger.info('Starting diff calculation')
        if self.old_path_is_file and self.new_path_is_file:
            change_pairs.append((self.old_path, self.new_path))
            return change_pairs
        elif self.old_path_is_file != self.new_path_is_file:
            self.logger.error('Datapaths are of different types')
            sys.exit()

        '''
        check if indexes on the data are present
        else, check for data types and invoke parallel comparison
        '''
        old_index_path = None
        new_index_path = None
        is_indexed = False
        indexdir = os.path.join(self.stagingdir, 'indexes')
        index_metafile = os.path.join(indexdir, 'INDEXED_PATHS')

        if os.path.exists(index_metafile):
            indexed_paths = dacman_utils.load_yaml(index_metafile)
            paths_indexed = [False, False]
            for path in indexed_paths:
                p = path + os.sep
                if self.old_path.startswith(p) or self.old_path == path:
                    old_index_path = os.path.join(indexdir, get_hash_id(os.path.abspath(path)))
                    paths_indexed[0] = True
                if self.new_path.startswith(p) or self.new_path == path:
                    new_index_path = os.path.join(indexdir, get_hash_id(os.path.abspath(path)))
                    paths_indexed[1] = True
                if all(paths_indexed):
                    is_indexed = True
                    break

        if is_indexed:
            changeManager = ChangeManager(self.old_path, self.new_path, False, self.stagingdir)
            status, cached_old_path, cached_new_path = changeManager.get_cached_paths()
            change_data = changeManager.get_changes(status, cached_old_path, cached_new_path)

            old_datapath_file = os.path.join(old_index_path, 'DATAPATH')
            new_datapath_file = os.path.join(new_index_path, 'DATAPATH')

            old_filelist = os.path.join(old_index_path, 'FILEPATHS')
            new_filelist = os.path.join(new_index_path, 'FILEPATHS')

            with open(old_datapath_file) as f:
                old_basepath = f.readline().split('\n')[0]

            with open(new_datapath_file) as f:
                new_basepath = f.readline().split('\n')[0]

            with open(old_filelist) as f:
                for relpath in f:
                    filepath = os.path.join(old_basepath, relpath)
                    if filepath == self.old_path:
                        self.old_path_is_file = True
                        break

            with open(new_filelist) as f:
                for relpath in f:
                    filepath = os.path.join(new_basepath, relpath)
                    if filepath == self.old_path:
                        self.new_path_is_file = True
                        break
        else:
            self.logger.warning('Datapaths are not indexed. Trying to locate and index the data...')

            '''
            The code below allows to check for a diff between any two random files
            '''
            # change_data = change.changes(old_base, new_base, False, self.stagingdir)
            changeManager = ChangeManager(old_base, new_base, False, self.stagingdir)
            status, cached_old_path, cached_new_path = changeManager.get_cached_paths()
            change_data = changeManager.get_changes(status, cached_old_path, cached_new_path)

        changes = change_data.modified

        self.logger.info('Searching for path indexes')

        '''
        find the old and new base directories which are indexed through
        '''
        path_prefix_new = cached_new_path
        path_prefix_old = cached_old_path
        '''
        save the metadata about the high-level diff between the directories
        '''
        if not self.old_path_is_file:
            if self.save_changes:
                self._save_dir_diff(change_data)
                self.logger.info('Change summary saved in: %s', self.outdir)
            change.display(change_data)
            '''
            for each file level change, a detailed change analysis is reqd
            '''
            for change_key in changes:
                new_path = os.path.join(path_prefix_new, change_key)
                old_path = os.path.join(path_prefix_old, changes[change_key])
                change_pairs.append((new_path, old_path))
        else:
            rel_new_path = os.path.relpath(self.new_path, path_prefix_new)
            rel_old_path = os.path.relpath(self.old_path, path_prefix_old)
            if rel_new_path in changes and changes[rel_new_path] == rel_old_path:
                change_pairs.append((self.new_path, self.old_path))

        return change_pairs

    '''
    saves directory changes
    '''
    def _save_dir_diff(self, change_data):
        SUMMARY_METAFILE = 'summary'
        ADDED_METAFILE = 'added'
        DELETED_METAFILE = 'deleted'
        MODIFIED_METAFILE = 'modified'
        METADATA_ONLY_METAFILE = 'metaonly'
        UNCHANGED_METAFILE = 'unchanged'

        self.logger.info('Saving summary of changes')
        outdir = self.outdir

        if not os.path.exists(outdir):
            os.makedirs(outdir)
        summary_file = os.path.join(outdir, SUMMARY_METAFILE)

        change_summary = {}
        change_summary['versions'] = {'base': {'dataset_id': change_data.old_path,
                                               'nfiles': change_data.old_nfiles},
                                      'revision': {'dataset_id': change_data.new_path,
                                                   'nfiles': change_data.new_nfiles}}
        change_summary['counts'] = change_data.get_change_map()
        dacman_utils.dump_yaml(change_summary, summary_file)

        add_change_file = os.path.join(outdir, ADDED_METAFILE)
        del_change_file = os.path.join(outdir, DELETED_METAFILE)
        mod_change_file = os.path.join(outdir, MODIFIED_METAFILE)
        meta_change_file = os.path.join(outdir, METADATA_ONLY_METAFILE)
        unchanged_meta_file = os.path.join(outdir, UNCHANGED_METAFILE)

        if len(change_data.added) > 0:
            dacman_utils.list_to_file(change_data.added, add_change_file)
        if len(change_data.deleted) > 0:
            dacman_utils.list_to_file(change_data.deleted, del_change_file)
        if len(change_data.modified) > 0:
            dacman_utils.dict_to_file(change_data.modified, mod_change_file)
        if len(change_data.metachange) > 0:
            dacman_utils.dict_to_file(change_data.metachange, meta_change_file)
        if len(change_data.unchanged) > 0:
            dacman_utils.list_to_file(change_data.unchanged, unchanged_meta_file)

    #########################################################################################################
    '''
    main diff function that calculates differences between files or directories
    '''
    def diff(self):
        if self.old_path == self.new_path:
            self.logger.error('Diff paths are the same')
            sys.exit()
        if self.executor == Executor.MPI:
            if not MPI4PY_IMPORT:
                print("mpi4py is not installed or possibly not in the path.")
                self.logger.error('mpi4py is not installed or possibly not in the path')
                sys.exit()
            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
            if rank == 0:
                self.logger.info('Runtime system = {}'.format(self.executor))
                change_pairs = self.get_change_pairs()
                if self._diff_all or self.old_path_is_file > 0:
                    differ = DataDiffer(change_pairs, self.executor)
                    differ.mpi_world = comm
                    differ.start()
                self.logger.info('Diff completed')
            else:
                if self._diff_all or self.old_path_is_file:
                    differ = DataDiffer(None, self.executor)
                    differ.mpi_world = comm
                    differ.start()
        else:
            self.logger.info('Runtime system = {}'.format(self.executor))
            change_pairs = self.get_change_pairs()
            if (self._diff_all or self.old_path_is_file) and len(change_pairs) > 0:
                differ = DataDiffer(change_pairs, self.executor)
                if self.custom_analyzer is not None:
                    differ.use_plugin(self.custom_analyzer)
                differ.start()
            self.logger.info('Diff completed')


#######################################################################

def main(args):
    oldpath = args.oldpath
    newpath = args.newpath
    stagingdir = args.stagingdir
    analyzer = args.plugin
    recursive = args.compare
    outdir = args.outdir
    executor = args.executor

    differ = Differ(recursive, analyzer, executor, outdir)
    differ.set_paths(oldpath, newpath, stagingdir)
    differ.diff()
