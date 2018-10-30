import sys
import os
import redis
import multiprocessing
import marshal
import subprocess
import logging
import numpy as np
from datetime import datetime

import stream_worker

try:
   from mpi4py import MPI
   MPI4PY_IMPORT = True
except ImportError:
   MPI4PY_IMPORT = False

__modulename__ = 'diffstream'

#startTime = datetime.now()

class DiffStream(object):
    DEFAULT_EXECUTOR = 0
    MPI_EXECUTOR = 1

    def __init__(self, host, port, db, redis_queue_id=None, custom_analyzer=None, executor=MPI_EXECUTOR):
        self.pool = None
        self.mpi_proc = None

        self.redis_queue_id = redis_queue_id
        self.custom_analyzer = custom_analyzer
        self.executor = executor

        self.host = host
        self.port = port
        self.db = db

        self.r = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db
        )

        self.logger = logging.getLogger(__name__)


#########################################################################################################

    def printProcStdout(self):
        '''
        Return a line from the subprocess that's running
        in the background
        '''
        if self.mpi_proc:
            for stdout_line in iter(self.mpi_proc.stdout.readline, ""):
                yield stdout_line
            #self.mpi_proc.stdout.close()

#########################################################################################################

    def start(self):
        '''
        Main function that starts the process of looking for tasks
        '''
        #### Use python multiprocessing if default executor
        if self.executor == DiffStream.DEFAULT_EXECUTOR:
            self.logger.info('Using Python multiprocessing for executing diffstream tasks')
            self.diff_tasks_default()
        #### Use MPI if specified
        elif self.executor == DiffStream.MPI_EXECUTOR:
            if not MPI4PY_IMPORT:
                self.logger.error('mpi4py is not installed or possibly not in the path')
                sys.exit()
            self.logger.info('Using MPI for executing diffstream tasks')
            self.diff_tasks_mpi()


    def stop(self):
        '''
        Stops the looking for tasks process
        '''
        #### Use python multiprocessing if default executor
        if self.executor == DiffStream.DEFAULT_EXECUTOR:
            if self.pool:
                try:
                    self.logger.info('Stopping Multiprocessing pool task handler process')
                    self.pool.close()
                    #self.pool.join()
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
        #### Use MPI if specified
        elif self.executor == DiffStream.MPI_EXECUTOR:
            if self.mpi_proc:
                try:
                    self.logger.info('Stopping MPI task handler process')
                    self.mpi_proc.kill()
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
            else:
                self.logger.info('No MPI process to stop')
        
        #print(datetime.now() - startTime)
        self.logger.info('Diff completed')



#########################################################################################################
    
    def diff_tasks_default(self):
        '''
        function to execute diff tasks using the default
        executor (Python multiprocessing).
        '''

        func_file = "func_analyzer_multiproc.marshal"

        with open(func_file, 'wb') as f:
            marshal.dump(self.custom_analyzer.__code__, f)
        
        worker_args = {
            'r_host': self.host,
            'r_port': self.port,
            'r_db': self.db,
            'redis_queue_id': self.redis_queue_id,
            'func_file': func_file,
            'executor': str(self.executor),
        }

        num_procs = multiprocessing.cpu_count()
        self.pool = multiprocessing.Pool(processes=num_procs)

        for i in range(num_procs):
            out_code = self.pool.apply_async(stream_worker.s_main, 
                args=(worker_args, ))


    def diff_tasks_mpi(self):
        '''
        function to execute diff tasks using the MPI
        executor.
        '''

        size = multiprocessing.cpu_count()

        func_file = "func_analyzer_mpi.marshal"

        with open(func_file, 'wb') as f:
            marshal.dump(self.custom_analyzer.__code__, f)

        worker_command = [
            "mpirun",
            "-n",
            str(size),
            "python",
            "stream_worker.py",
            str(self.host),
            str(self.port),
            str(self.db),
            self.redis_queue_id,
            func_file,
            str(self.executor)
        ]

        self.mpi_proc = subprocess.Popen(worker_command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
                                #universal_newlines=True)


#########################################################################################################

def main(args):
    redis_queue_id = args.redis_queue_id
    analyzer = args.analyzer

    executor_map = {'default': DiffStream.DEFAULT_EXECUTOR,
                    'mpi': DiffStream.MPI_EXECUTOR,}
    executor = executor_map[args.executor]

    diffstream = DiffStream(redis_queue_id=redis_queue_id, custom_analyzer=analyzer, executor=executor)
    diffstream.start()

def s_main(args):
    redis_queue_id = args['redis_queue_id']
    analyzer = args['analyzer']

    diffstream = DiffStream(redis_queue_id=redis_queue_id, custom_analyzer=analyzer)
    diffstream.start()

if __name__ == '__main__':
    #print(sys.argv)
    #args = {'redis_queue_id': sys.argv[1], 'analyzer': sys.argv[2]}

    args = {'redis_queue_id': sys.argv[1], 'analyzer': two_frame_analysis}

    s_main(args)
