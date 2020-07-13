import _thread
from dacman_stream.cache import Cache

# StreamSource Implementation
class DacmanWorker(object):
    def __init__(self, host, port):
        self.cache = Cache(host, port)
        self.wait_time = 10
        self.max_failed_count = 10
        self.analysis_operator = None

        self.stats_dir = None

    def set_wait_time(self, wait_time):
        self.wait_time = wait_time

    def set_max_failed_count(self, max_failed_count):
        self.max_failed_count = max_failed_count

    def set_stats_dir(self, stats_dir):
        self.stats_dir = stats_dir

    def set_analysis_operator(self, fn):
        self.analysis_operator = fn

    def process_task(self, task_entry):
        '''
        Actual execution logic that calls the custom analyzer
        for processing -Each worker is executing this function-
        where this processes a single task.
        '''
        #task_uuid, data_id1, data_id2, protocol = eval(task_entry)
        task = eval(task_entry)

        task_uuid = task[0]
        datablock_ids = task[1:]

        datablocks = self.cache.dataid_to_datablock(task_uuid, *datablock_ids)

        results = self.analysis_operator(*datablocks)
        self.cache.put_results(task_uuid, *results)

    def process(self):
        '''
        Main Processing Engine
        '''
        if not self.analysis_operator:
            raise ValueError("analysis operator must be set")

        # Count the number of failed brpop to end the 
        # process eventually
        failed_count = 0

        # Set a key to show that the worker is alive
        self.cache.worker_ready()

        while (failed_count < self.max_failed_count):
            # redis's BRPOP command is useful here as it 
            # will block on redis till it return a task
            # Note timeout is in seconds. Default 10 secs
            task = self.cache.pull_task(self.wait_time)
            if task:
                failed_count = 0
                
                self.process_task(task[1])
            else:
                print("Queue is empty")
                failed_count += 1

                if failed_count == 5 and self.stats_dir:
                    print(rank, "Writing to csv to", output_dir, end='\n\n')
                    _thread.start_new_thread(self.cache.write_wroker_stats, (self.stats_dir,))
