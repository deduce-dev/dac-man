import sys
import os
import time
import redis
import multiprocessing
import marshal
import subprocess
import _thread
import logging
import numpy as np
from datetime import datetime

import stream_worker

import settings as _settings

try:
   from mpi4py import MPI
   MPI4PY_IMPORT = True
except ImportError:
   MPI4PY_IMPORT = False

__modulename__ = 'workersmanager'

#startTime = datetime.now()

class WorkersManager(object):
    DEFAULT_EXECUTOR = 0
    MPI_EXECUTOR = 1

    def __init__(self, redis_queue_id=None, custom_analyzer_file=None, executor=MPI_EXECUTOR):
        self.pool = None
        self.mpi_proc = None

        self.redis_queue_id = self.get_redis_queue_id(redis_queue_id)
        self.custom_analyzer_file = self.get_custom_analyzer_file(custom_analyzer_file)
        self.executor = executor

        self.host = _settings.HOST
        self.port = _settings.PORT
        self.db = _settings.DATABASE    

        self.logger = logging.getLogger(__name__)


    def get_redis_queue_id(self, redis_queue_id):
        '''
        Get redis_queue_id from settings.py if redis_queue_id is None.
        '''
        if redis_queue_id:
            return redis_queue_id
        else:
            return str(_settings.TASK_QUEUE_NAME + ":" + _settings.REDIS_QUEUE_ID)

    def get_custom_analyzer_file(self, custom_analyzer_file):
        '''
        Get redis_queue_id from settings.py if redis_queue_id is None.
        '''
        if custom_analyzer_file:
            return custom_analyzer_file
        else:
            return _settings.CUSTOM_ANALYZER_FILE


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

    def printProcLine(self):
        for line in self.printProcStdout():
            if line != b'':
                print(line)

#########################################################################################################

    def start(self):
        '''
        Main function that starts the process of looking for tasks
        '''
        #### Use python multiprocessing if default executor
        if self.executor == WorkersManager.DEFAULT_EXECUTOR:
            self.logger.info('Using Python multiprocessing for executing WorkersManager tasks')
            self.diff_tasks_default()
        #### Use MPI if specified
        elif self.executor == WorkersManager.MPI_EXECUTOR:
            if not MPI4PY_IMPORT:
                self.logger.error('mpi4py is not installed or possibly not in the path')
                sys.exit()
            self.logger.info('Using MPI for executing WorkersManager tasks')
            self.diff_tasks_mpi()

        _thread.start_new_thread(self.printProcLine, ())
        print("WorkersManager.start(): Before Sleep")
        time.sleep(300)
        print("WorkersManager.start(): After Sleep")
        #### Stop all the processes (Still Testing)
        self.stop()


    def stop(self):
        '''
        Stops the looking for tasks process
        '''
        #### Use python multiprocessing if default executor
        if self.executor == WorkersManager.DEFAULT_EXECUTOR:
            if self.pool:
                try:
                    self.logger.info('Stopping Multiprocessing pool task handler process')
                    self.pool.close()
                    #self.pool.join()
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
        #### Use MPI if specified
        elif self.executor == WorkersManager.MPI_EXECUTOR:
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
        
        worker_args = {
            'r_host': self.host,
            'r_port': self.port,
            'r_db': self.db,
            'redis_queue_id': self.redis_queue_id,
            'func_file': self.custom_analyzer_file,
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

        worker_command = [
            "mpirun",
            "-n",
            str(size),
            "python3",
            "stream_worker.py",
            str(self.host),
            str(self.port),
            str(self.db),
            self.redis_queue_id,
            self.custom_analyzer_file,
            str(self.executor)
        ]

        self.mpi_proc = subprocess.Popen(worker_command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
                                #universal_newlines=True)


#########################################################################################################

def s_main():
    workers_manager = WorkersManager()
    workers_manager.start()

if __name__ == '__main__':
    s_main()
