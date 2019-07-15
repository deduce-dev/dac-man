import sys
import traceback
import redis
import multiprocessing
import marshal, types
import numpy as np

from mpi4py import MPI

from math import sqrt
from scipy import stats
from sklearn.metrics import mean_squared_error

def get_redis_instance(host, port, db):
    '''
    Return a redis instance with the given config
    '''
    r = redis.Redis(
        host=host,
        port=port,
        db=db
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
    data1 = np.fromstring(r.get(data_id1), dtype='<f4')
    data2 = np.fromstring(r.get(data_id2), dtype='<f4')

    return data1, data2


def process_task(r, task, custom_analyzer):
    '''
    Actual execution logic that calls the custom analyzer
    for processing -Each worker is executing this function-
    where this processes an single task.
    '''
    task_uuid, data_id1, data_id2, protocol = eval(task)

    data1, data2 = dataid_to_datablock(r, data_id1, data_id2)

    try:
        r.set(task_uuid, (custom_analyzer(data1, data2)))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    return 1


#def diff_tasks(r, redis_queue_id, custom_analyzer, is_mpi=False, 
#                func_file= None, r_host=None, r_port=None, r_db=None):
def diff_tasks(r, redis_queue_id, custom_analyzer, is_mpi=False):
        '''
        function to execute diff tasks.
        '''

        #if r == None:
        #    r = get_redis_instance(r_host, r_port, r_db)

        #if custom_analyzer == None:
        #    custom_analyzer = get_redis_instance(r_host, r_port, r_db)

        if is_mpi:
            comm = MPI.COMM_WORLD
            rank = "%s-%s"  % ("MPIWorker", comm.Get_rank())
        else:
            current = multiprocessing.current_process()
            rank = current.name
            #print("diff_tasks rank:", rank)

        #### Count the number of failed brpop to end the 
        #### process eventually
        failed_count = 0

        #### Wait for an hour and reset if a task is popped
        while (failed_count < 360):
            #### redis's BRPOP command is useful here as it 
            #### will block on redis till it return a task
            #### Note: timeout here is 10 seconds
            task = r.brpop(redis_queue_id, 10)
            if task:
                failed_count = 0

                print(rank, "is processing task:", task[1], end='\n\n')
                try:
                    out_code = process_task(r, task[1], custom_analyzer)
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    traceback.print_exc()
                    raise
            else:
                print("Queue is empty")
                failed_count += 1



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

    func_file = args['func_file']
    executor = args['executor']

    is_mpi = executor.isdigit() and int(executor) == 1

    custom_analyzer = func_deserializer_file(func_file)

    try:
        r = get_redis_instance(host, port, db)
        diff_tasks(r, redis_queue_id, custom_analyzer, is_mpi)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


if __name__ == '__main__':
    args = {
        'r_host': sys.argv[1],
        'r_port': sys.argv[2],
        'r_db': sys.argv[3],
        'redis_queue_id': sys.argv[4],
        'func_file': sys.argv[5],
        'executor': sys.argv[6],
    }

    s_main(args)