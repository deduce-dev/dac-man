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

import config as _config

try:
   from mpi4py import MPI
   MPI4PY_IMPORT = True
except ImportError:
   MPI4PY_IMPORT = False

__modulename__ = 'workersmanager'


logger = logging.getLogger(__name__)

def setup_logging(
    default_path='config/logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


class WorkersManager(object):
    def __init__(self):
        self.pool = None
        self.mpi_proc = None
        self.r = None

        self.process_started = False


    def read_config(self):
        '''
        Read needed values from config.py
        '''
        self.redis_queue_id = str(_config.TASK_QUEUE_NAME + ":" + _config.REDIS_QUEUE_ID)

        #### Get the file that has the analyzer function serialization 
        #### from config.py.
        self.custom_analyzer_file = _config.CUSTOM_ANALYZER_FILE

        self.executor = _config.EXECUTOR

        if not self.r:
            self.host = _config.HOST
            self.port = _config.PORT
            self.db = _config.DATABASE

            self.r = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db
            )



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
                logger.debug(line)

#########################################################################################################

    def start(self):
        '''
        Main function that starts the process of looking for tasks
        '''
        while True:
            logger.debug("Reading Config")
            self.read_config()

            no_change_count = 0
            r_queue_len = self.r.llen(self.redis_queue_id)
            temp_len = r_queue_len
            while r_queue_len > 0:
                if not self.process_started:
                    self.execute()
                    self.process_started = True
                    ## Check if we need to kill that thread.
                    ## I am assuming that the thread will end by when
                    ## the function execution ends
                    _thread.start_new_thread(self.printProcLine, ())

                time.sleep(5)
                logger.debug("Number of Tasks in Queue: %s" \
                    % str(self.r.llen(self.redis_queue_id)))

                #### Check if the len of the redis queue didn't change
                #### for 2 mins
                if r_queue_len == temp_len:
                    if no_change_count >= 24:
                        no_change_count = 0
                        logger.debug("Calling self.stop()")
                        self.stop()
                        self.process_started = False
                    else:
                        no_change_count += 1

                temp_len = r_queue_len
                r_queue_len = self.r.llen(self.redis_queue_id)
 
            time.sleep(10)

            if self.process_started:
                logger.debug("Calling self.stop()")
                self.stop()
                self.process_started = False


    def execute(self):
        '''
        Start executing tasks through the chosen executor method
        '''
        #### Use python multiprocessing if default executor
        if self.executor == _config.DEFAULT_EXECUTOR:
            logger.info('Using Python multiprocessing for executing WorkersManager tasks')
            self.diff_tasks_default()
        #### Use MPI if specified
        elif self.executor == _config.MPI_EXECUTOR:
            if not MPI4PY_IMPORT:
                logger.error('mpi4py is not installed or possibly not in the path')
                sys.exit()
            logger.info('Using MPI for executing WorkersManager tasks')
            self.diff_tasks_mpi()


    def stop(self):
        '''
        Stops the looking for tasks process
        '''
        #### Use python multiprocessing if default executor
        if self.executor == _config.DEFAULT_EXECUTOR:
            if self.pool:
                try:
                    logger.info('Stopping Multiprocessing pool task handler process')
                    self.pool.close()
                    #self.pool.join()
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
        #### Use MPI if specified
        elif self.executor == _config.MPI_EXECUTOR:
            if self.mpi_proc:
                try:
                    logger.info('Stopping MPI task handler process')
                    self.mpi_proc.kill()
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
            else:
                logger.info('No MPI process to stop')
        
        #print(datetime.now() - startTime)
        logger.info('Diff completed')



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
        #### change for NERSC as the number of workers is
        #### specified externally
        size = 1

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
    setup_logging(default_level=logging.DEBUG)

    '''
    if (len(sys.argv) < 4):
            print("Usage: python workers_manager.py <redis_host> <redis_port> <redis_db>")
    else:
        redis_host = os.path.abspath(sys.argv[1])
        redis_port = sys.argv[2]
        redis_db = os.path.abspath(sys.argv[3])
    '''

    s_main()
