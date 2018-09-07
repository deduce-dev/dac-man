"""
`dacman.core.mpi_indexer`
====================================

.. currentmodule:: dacman.core.mpi_indexer

:platform: Unix, Mac
:synopsis: MPI module for parallel indexing

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

import yaml
import sys
import os
import hashlib
import time

try:
    from mpi4py import MPI
    __AVAIL_MPI__ = True
except ImportError:
    __AVAIL_MPI__ = False

import multiprocessing

import dacman.core.scanner as scanner
from dacman.core.utils import cprint, dict_to_file
import dacman.core.utils as dacman_utils

import logging

__modulename__ = 'indexer'

logger = logging.getLogger(__name__)

## DIRTY_CODING: redundant functions in indexer and mpi_indexer
## TODO: cleanup and merge, but MPI and non-MPI code work differently.

def get_data_files(deduce_metadata):
    with open(deduce_metadata, 'r') as f:
        meta_yaml = yaml.load(f)
        file_list = meta_yaml.keys()
        return file_list    


def dump(data, filepath):
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    

def calculate_hash(datapath, filename):
    file_path = os.path.join(datapath, filename)
    checksum = hashlib.md5()
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(4096), b""):
            checksum.update(block)

    file_hash = checksum.hexdigest()
    return (filename, file_hash)


def read_filelist(metafile):
    logger.info('Getting file list')
    with open(metafile) as f:
        filelist = f.readlines()
        
    filelist = [s.strip() for s in filelist]
    return filelist

    
def check_deducedir(custom_deducedir, datapath):
    if not os.path.exists(datapath):
        logger.error('Datapath %s does not exist!', datapath)
        sys.exit()

    if not os.path.isdir(datapath):
        logger.error('Cannot index a standalone file, only data directories can be indexed')
        sys.exit()

    if not custom_deducedir:        
        #deducedir = os.path.join(datapath, '.deduce')
        deducedir = dacman_utils.DACMAN_STAGING_LOC
    else:
        deducedir = custom_deducedir

    deducedir = os.path.join(deducedir, get_hash_id(datapath))

    if not os.path.exists(deducedir):
        os.makedirs(deducedir)

    return deducedir


def index(datapath, custom_deducedir):
    logger.info('Indexing %s', datapath)
    if __AVAIL_MPI__:
        logger.info('Using MPI for parallel indexing')
        mpi_index(custom_deducedir, datapath)
    else:
        logger.error('mpi4py is not installed or not in path')
        sys.exit()

def save_indexes(deducedir, indexes):
    '''
    There are two types of indexes created for each data path.
    First, a hash of the data in a file to the file path.
    Second, a file path to its hash.
    A map of filename to all the paths is also created.
    '''
    logger.info('Building two-way hash indexes')
    indexpath = os.path.join(deducedir, 'indexes')
    if not os.path.exists(indexpath):
        os.makedirs(indexpath)
    path_index_file = os.path.join(indexpath, 'PATH.idx')
    data_index_file = os.path.join(indexpath, 'DATA.idx')
    name_path_map_file = os.path.join(indexpath, 'PATHNAME.map')
    path_indexes = dict(indexes)
    data_indexes = {}
    name_path_map = {}
    for k, v in path_indexes.items():
        data_indexes[v] = k
        filename = os.path.basename(k)
        if filename in name_path_map:
            name_path_map[filename] = name_path_map[filename] + ' ' + k
        else:
            name_path_map[filename] = k
    logger.info('Saving indexes')
    dict_to_file(path_indexes, path_index_file)
    dict_to_file(data_indexes, data_index_file)
    dict_to_file(name_path_map, name_path_map_file)
    logger.info('Directory indexing complete')


'''
function to index file paths in parallel using MPI for scaling
across multiple nodes in a cluster
'''
def mpi_index(custom_deducedir, datapath):    
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    status = MPI.Status()
    
    class States():
        READY = 0
        START = 1
        DONE = 2
        EXIT = 3

    if rank == 0:
        deducedir = check_deducedir(custom_deducedir, datapath)
        '''
        deduce_metadata = os.path.join(deducedir, 'METADATA')
        if not os.path.exists(deduce_metadata):
        scanner.scan(datapath, deducedir)
        '''
        deduce_file = os.path.join(deducedir, 'FILEPATHS')
        if not os.path.exists(deduce_file):
            scanner.scan(datapath, os.path.dirname(deducedir))

        filelist = []
        file_num = 0
        closed_workers = 0
        num_workers = size - 1
        indexes = []

        filelist = read_filelist(deduce_file)

        logger.info('Indexing %d files', len(filelist))
        while closed_workers < num_workers:
            result = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            source = status.Get_source()
            tag = status.Get_tag()
            
            if tag == States.READY:
                if file_num < len(filelist):
                    comm.send(filelist[file_num], dest=source, tag=States.START)
                    file_num += 1
                else:
                    comm.send(None, dest=source, tag=States.EXIT)
            elif tag == States.DONE:
                indexes.append(result)
            elif tag == States.EXIT:
                closed_workers += 1

        save_indexes(deducedir, indexes)
    else:
        while True:
            comm.send(None, dest=0, tag=States.READY)
            filename = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()

            if tag == States.START:
                index = calculate_hash(datapath, filename)
                comm.send(index, dest=0, tag=States.DONE)
            elif tag == States.EXIT:
                comm.send(None, dest=0, tag=States.EXIT)
                break

def main(args):
    datapath = os.path.abspath(args.datapath)
    deducedir = args.deducedir
    index(datapath, deducedir)

def s_main(args):
    datapath = args['datapath']
    deducedir = None
    if 'deducedir' in args:
       deducedir = args['deducedir']

    index(datapath, deducedir)

if __name__ == '__main__':
   args = {'datapath': sys.argv[1]}

   s_main(args)
