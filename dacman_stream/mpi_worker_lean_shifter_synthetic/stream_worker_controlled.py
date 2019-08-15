import os
import sys
import time
import traceback
import redis
import socket
import multiprocessing
import marshal, types
import _thread
import numpy as np

from mpi4py import MPI

from math import sqrt
from scipy import stats
from sklearn.metrics import mean_squared_error

import csv

import config as _config

data_pull_start = {}
data_pull_end = {}
job_end_processing = {}
job_end_data_put = {}

def get_diff(a, b):
    return np.subtract(b, a)

def get_redis_instance(host, port, db):
    '''
    Return a redis instance with the given config
    '''
    r = redis.Redis(
        host=host,
        port=port
    )

    return r


def func_deserializer(ser_analyzer):
    '''
    Deserialize analyzer function
    '''
    code = marshal.loads(ser_analyzer)
    func = types.FunctionType(code, globals(), "analyzer")

    return func

def func_deserializer_file(file):
    '''
    Deserialize analyzer function from a file
    '''
    with open(file, 'rb') as f:
        code = marshal.load(f)
    func = types.FunctionType(code, globals(), "analyzer")

    return func


def dataid_to_datablock(r, data_id1, data_id2):
    '''
    Retrieves DataBlocks from given Data IDs
    '''
    #data1 = np.fromstring(r.get(data_id1), dtype='<f4')
    #data2 = np.fromstring(r.get(data_id2), dtype='<f4')
    data1, data2 = r.mget([data_id1, data_id2])

    #p = r.pipeline()
    #p.mget([data_id1, data_id2])
    #p.delete(data_id1)
    #response = p.execute()

    #data1, data2 = response[0]

    data1 = np.fromstring(data1, dtype='<f4')
    data2 = np.fromstring(data2, dtype='<f4')

    return data1, data2


def process_task(r, task, custom_analyzer):
    '''
    Actual execution logic that calls the custom analyzer
    for processing -Each worker is executing this function-
    where this processes an single task.
    '''
    task_uuid, data_id1, data_id2, protocol = eval(task)

    data_pull_start[task_uuid] = time.time()

    data1, data2 = dataid_to_datablock(r, data_id1, data_id2)

    data_pull_end[task_uuid] = time.time()

    try:
        rms_log, t_test_t, t_test_p = custom_analyzer(data1, data2)
        job_end_processing[task_uuid] = time.time()
        r.set(task_uuid, (rms_log, t_test_t, t_test_p))
        job_end_data_put[task_uuid] = time.time()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    return 1

def write_to_csv():
    output_dir_path = _config.OUTPUT_CSV_DIR

    name = _config.CSV_DICTS_DIRS[0]
    output_full_path = os.path.join(output_dir_path, name, 
            '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in data_pull_start.items():
            writer.writerow([key, value])

    name = _config.CSV_DICTS_DIRS[1]
    output_full_path = os.path.join(output_dir_path, name, 
            '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in data_pull_end.items():
            writer.writerow([key, value])

    name = _config.CSV_DICTS_DIRS[2]
    output_full_path = os.path.join(output_dir_path, name, 
            '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in job_end_processing.items():
            writer.writerow([key, value])

    name = _config.CSV_DICTS_DIRS[3]
    output_full_path = os.path.join(output_dir_path, name, 
            '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in job_end_data_put.items():
            writer.writerow([key, value])


#def diff_tasks(r, redis_queue_id, custom_analyzer, is_mpi=False, 
#                func_file= None, r_host=None, r_port=None, r_db=None):
def diff_tasks(r, redis_queue_id, custom_analyzer, start_at_num, is_mpi=False):
        '''
        function to execute diff tasks.
        '''

        #if r == None:
        #    r = get_redis_instance(r_host, r_port, r_db)

        #if custom_analyzer == None:
        #    custom_analyzer = get_redis_instance(r_host, r_port, r_db)

        if is_mpi:
            comm = MPI.COMM_WORLD
            rank = "%s:%s-%s:%s-%s:%s"  % ("Host", socket.gethostname(), 
                    "PID", os.getpid(), "MPIWorker", comm.Get_rank())
        else:
            current = multiprocessing.current_process()
            rank = current.name
            #print("diff_tasks rank:", rank)

        #### Count the number of failed brpop to end the 
        #### process eventually
        failed_count = 0

        #### Set a key to show that the worker is alive
        r.set("worker", 1)

        #### Controlled experiment where the workers don't start
        #### till there's start_at_num numbers of jobs
        while r.llen(redis_queue_id) < start_at_num:
            time.sleep(1)

        #### Wait for an hour and reset if a task is popped
        #while (failed_count < 360):
        #### Wait for 120 seconds and reset if a task is popped
        #while (failed_count < 12):
        #### Wait for 25 mins and reset if a task is popped
        while (failed_count < 150):
            #### redis's BRPOP command is useful here as it 
            #### will block on redis till it return a task
            #### Note: timeout here is 10 seconds
            task = r.brpop(redis_queue_id, 10)
            #task = r.rpop(redis_queue_id)
            if task:
                failed_count = 0

                print(rank, "is processing task:", task[1], end='\n\n')
                #print(rank, "is processing task:", task, end='\n\n')
                try:
                    out_code = process_task(r, task[1], custom_analyzer)
                    #out_code = process_task(r, task, custom_analyzer)
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    traceback.print_exc()
                    raise
            else:
                print("Queue is empty")
                failed_count += 1
                time.sleep(1)

                if failed_count == 5:
                    _thread.start_new_thread(write_to_csv, ())
                


#########################################################################################################

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def s_main(args):

    host = args['r_host']
    port = args['r_port']
    db =  args['r_db']

    redis_queue_id = args['redis_queue_id']
    #custom_analyzer = func_deserializer(args['analyzer_string'])

    start_at_num = args['start_at']

    func_file = args['func_file']
    executor = args['executor']

    is_mpi = executor.isdigit() and int(executor) == 1
    #### As we are using NERSC shifter, it's going to be
    #### always mpi
    is_mpi = True

    #custom_analyzer = func_deserializer_file(func_file)
    custom_analyzer = get_diff

    try:
        r = get_redis_instance(host, port, db)
        diff_tasks(r, redis_queue_id, custom_analyzer, start_at_num, is_mpi)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


if __name__ == '__main__':
    args = {
        'r_host': sys.argv[1],
        'r_port': sys.argv[2],
        'r_db': sys.argv[3],
        'redis_queue_id': sys.argv[4],
        'start_at': int(sys.argv[5])
    }

    args['func_file'] = str(_config.CUSTOM_ANALYZER_FILE)
    args['executor'] = str(_config.EXECUTOR)

    s_main(args)
