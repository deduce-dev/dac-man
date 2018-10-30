import os
import sys
import h5py
import redis
import copy
import uuid
import multiprocessing
import numpy as np
from datetime import datetime
from hashlib import blake2b
from math import sqrt
from scipy import stats
from mpi4py import MPI
from sklearn.metrics import mean_squared_error

import settings as _settings

r = redis.Redis(
    host=_settings.HOST,
    port=_settings.PORT,
    db=_settings.DATABASE
)

startTime = datetime.now()

def two_frame_analysis(dataA, dataB):
    rms_log = None
    t_test_t = None
    t_test_p = None
    do_ttest = True

    matrix1 = dataA
    matrix2 = dataB

    #matrix1 = dataA.flatten()
    #matrix2 = dataB.flatten()

    rms = sqrt(mean_squared_error(matrix1, matrix2)) #compute RMSE between the 2 input frames
    min_d = min(min(matrix1), min(matrix2))
    max_d = max(max(matrix1), max(matrix2))
    
    rms_log = np.log(rms) #logarithm of RMSE

    if do_ttest:
        #option 1: t-test over the whole frame
        t_test_t, t_test_p = stats.ttest_ind(matrix1, matrix2, equal_var=True)
    
    return rms_log, t_test_t, t_test_p


def dataid_to_datablock(data_id1, data_id2):
    data1 = np.fromstring(r.get(data_id1), dtype='<f4')
    data2 = np.fromstring(r.get(data_id2), dtype='<f4')

    return data1, data2


def process_task(task):
    task_uuid, data_id1, data_id2, protocol = eval(task)
    data1, data2 = dataid_to_datablock(data_id1, data_id2)

    #if protocol == "custom":
    #    rms, t_test_t, t_test_p = two_frame_analysis(data1, data2)

    #print(multiprocessing.current_process(), "rms:", rms, "t_test_t:", t_test_t, "t_test_p:", t_test_p)

    task_output_hash_str = task_uuid
    #r.set(task_output_hash_str, (rms, t_test_t, t_test_p))
    r.set(task_output_hash_str, (two_frame_analysis(data1, data2)))

    return 1


def diff_tasks_default(redis_queue_id):
    '''
    function to execute diff tasks using the default
    executor (Python multiprocessing).
    '''
    num_procs = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_procs)
    
    while (r.llen(task_queue_hash_string) > 0):
    #while (True):
        #### For Multi-Processing ####
        #print("Waiting for Task")
        #print(r.brpop(redis_queue_id, 10))
        out_code = pool.apply_async(process_task, 
            args=(r.brpop(redis_queue_id), ))

        ## Calling .get() here makes the code block till it get
        ## result.. That's why it commented out
        #task_uuid, rms, t_test_t, t_test_p = result.get()
        #### End of Mulit-Processing ####

    pool.close()
    pool.join()


def diff_tasks_mpi(redis_queue_id):
    '''
    function to execute diff tasks using the MPI
    executor.
    '''
    #### For MPI Processing ####
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    status = MPI.Status()

    while (r.llen(task_queue_hash_string) > 0):
        out_code = process_task(r.brpop(redis_queue_id))


if __name__ == "__main__":

    hash_task_queue = blake2b(digest_size=20)
    hash_task_queue.update(_settings.TASK_QUEUE_NAME.encode('utf-8'))
    task_queue_hash_string = "%s:%s" % (_settings.TASK_QUEUE_NAME, hash_task_queue.hexdigest())

    diff_tasks_default(task_queue_hash_string)
    #diff_tasks_mpi(task_queue_hash_string)

    #print("Normal")

    #### For Multi-Processing ####
    #num_procs = multiprocessing.cpu_count()
    #print("num_procs:", num_procs)
    #pool = multiprocessing.Pool(processes=num_procs)
    #### End of Mulit-Processing ####

    '''
    #### For MPI Processing ####
    #MPI.Init()
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    status = MPI.Status()
    #### End of MPI Processing ####

    while (r.llen(task_queue_hash_string) > 0):
        # Time taken to finish the "" dataset by several methods
        # Pool: 0:03:35.161539
        # Normal (1): 0:03:39.588023
        # Pool (2): 0:01:34.140991
        # Pool (3): 0:01:28.592517
        # MPI (1): 0:01:16.359235

        #### For Multi-Processing ####
        #result = pool.apply_async(process_task, args=(r.rpop(task_queue_hash_string), ))

        ## Calling .get() here makes the code block till it get
        ## result.. That's why it commented out
        #task_uuid, rms, t_test_t, t_test_p = result.get()
        #### End of Mulit-Processing ####

        #### For Normal Processing ####
        #task_uuid, rms, t_test_t, t_test_p = process_task(r.rpop(task_queue_hash_string))
        #### End of Normal Processing ####

        #### For MPI Processing ####
        out_code = process_task(r.rpop(task_queue_hash_string))
        #### End of MPI Processing ####

    #### For Multi-Processing ####
    #pool.close()
    #pool.join()
    #### End of Mulit-Processing ####
    '''

    print(datetime.now() - startTime)
