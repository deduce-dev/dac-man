"""
`dacman.core.indexer`
====================================

.. currentmodule:: dacman.core.indexer

:platform: Unix, Mac
:synopsis: Module for indexing data on a desktop

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

import yaml
import sys
import os
import hashlib
import time

import multiprocessing
try:
    import tigres
    TIGRES_IMPORT = True
except ImportError:
    TIGRES_IMPORT = False

import dacman.core.scanner as scanner
from dacman.core.utils import cprint, dict_to_file, get_hash_id
import dacman.core.utils as dacman_utils

import logging

__modulename__ = 'indexer'

logger = logging.getLogger(__name__)

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
        deducedir = dacman_utils.DACMAN_STAGING_LOC
    else:
        deducedir = custom_deducedir

    deducedir = os.path.join(deducedir, get_hash_id(datapath))

    if not os.path.exists(deducedir):
        os.makedirs(deducedir)

    return deducedir

'''
main function to call different managers for parallel indexing
'''
def index(datapath, custom_deducedir=None, manager='python'):
    logger.info('Indexing %s', datapath)
    deducedir = check_deducedir(custom_deducedir, datapath)
    if manager == 'tigres':
        if not TIGRES_IMPORT:
            logger.error('Tigres is not installed or not in path')
            sys.exit()
        logger.info('Using Tigres for parallel indexing')
        tigres_index(deducedir, datapath)
    else:
        logger.info('Using Python multiprocessing for parallel indexing')
        mp_index(deducedir, datapath)

    return deducedir

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
function to index file paths in parallel using python multiprocessing
module
'''
def mp_index(deducedir, datapath):
    deduce_file = os.path.join(deducedir, 'FILEPATHS')
    if not os.path.exists(deduce_file):
        scanner.scan(datapath, os.path.dirname(deducedir))

    filelist = read_filelist(deduce_file)
    
    logger.info('Indexing %d files', len(filelist))
    num_procs = multiprocessing.cpu_count()
    results = []
    pool = multiprocessing.Pool(processes=num_procs)
    for filename in filelist:
        result = pool.apply_async(calculate_hash, args=(datapath, filename))
        results.append(result)

    pool.close()
    pool.join()
    indexes = [result.get() for result in results]

    save_indexes(deducedir, indexes)

'''
indexing using Tigres API for scaling across multiple nodes
'''
def tigres_index(deducedir, datapath):
    deduce_file = os.path.join(deducedir, 'FILEPATHS')
    if not os.path.exists(deduce_file):
        scanner.scan(datapath, os.path.dirname(deducedir))

    filelist = read_filelist(deduce_file)
    
    exec_name = 'EXECUTION_DISTRIBUTE_PROCESS'
    exec_plugin = tigres.utils.Execution.get(exec_name)

    try:
        logfile = 'deduce_index_{}.log'.format(round(time.time()))
        tigres.start(name='deduce_index', log_dest=logfile, execution=exec_plugin)
        tigres.set_log_level(tigres.Level.ERROR)

        task_array = tigres.TaskArray(tasks=[])
        
        task_hash = tigres.Task("hash_index", task_type=tigres.FUNCTION, impl_name=calculate_hash)
        task_array.append(task_hash)
        
        input_list = []
        for file in filelist:
            input_list.append([datapath, file])
        input_array = tigres.InputArray(values=input_list)

        logger.info('Indexing %d files', len(filelist))
        indexes = tigres.parallel('index_files', input_array=input_array, task_array=task_array)

        save_indexes(deducedir, indexes)

    except tigres.utils.TigresException as e:
        print(str(e))
        return_code = 1    

    tigres.end()


def main(args):
    datapath = os.path.abspath(args.datapath)
    deducedir = None
    if args.stagingdir is not None:
        #deducedir = os.path.join(args.stagingdir, os.path.basename(args.datapath)) 
        deducedir = args.stagingdir
    #args.stagingdir
    manager = args.manager
    index(datapath, deducedir, manager)

def s_main(args):
    datapath = args['datapath']
    deducedir = None
    if 'deducedir' in args:
       deducedir = args['deducedir']

    index(datapath, deducedir)

if __name__ == '__main__':
   args = {'datapath': sys.argv[1]}

   s_main(args)
