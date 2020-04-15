import os
import csv
import math
import numpy as np
import settings as _settings

from collections import defaultdict

class TaskStatGenerator(object):
    def __init__(self):
        self._sources_dir_name = _settings.SOURCE_DIR
        self._workers_dir_name = _settings.WORKER_DIR
        self._data_task_send_start = _settings.CSV_SOURCE_DICTS_DIRS[0]
        self._data_task_send_end = _settings.CSV_SOURCE_DICTS_DIRS[1]
        self._data_pull_start = _settings.CSV_WORKER_DICTS_DIRS[0]
        self._data_pull_end = _settings.CSV_WORKER_DICTS_DIRS[1]
        self._job_end_processing = _settings.CSV_WORKER_DICTS_DIRS[2]
        self._job_end_data_put = _settings.CSV_WORKER_DICTS_DIRS[3]

        self._setup_names = []
        self.xticks_labels = []


    def get_xticks_labels(self):
        '''
        Return results
        '''
        return self.xticks_labels

    def process(self, experiment_paths):
        '''
        Main orchestrating function
        '''
        stats = []
        for exp_p in experiment_paths:
            exp_stats = []
            for entry in os.scandir(exp_p):
                if entry.is_dir(follow_symlinks=False):
                    sources_dir = os.path.join(entry, self._sources_dir_name)
                    workers_dir = os.path.join(entry, self._workers_dir_name)

                    print("*******************************************************************")

                    print("sources_dir:", sources_dir)
                    print("workers_dir:", workers_dir)

                    data_task_send_start_dir = os.path.join(sources_dir, self._data_task_send_start)
                    data_task_send_end_dir = os.path.join(sources_dir, self._data_task_send_end)

                    data_pull_start_dir = os.path.join(workers_dir, self._data_pull_start)
                    data_pull_end_dir = os.path.join(workers_dir, self._data_pull_end)
                    job_end_processing_dir = os.path.join(workers_dir, self._job_end_processing)
                    job_end_data_put_dir = os.path.join(workers_dir, self._job_end_data_put)

                    exp_stats.append(
                        self.start_stats_calculation(
                            data_task_send_start_dir,
                            data_task_send_end_dir,
                            data_pull_start_dir,
                            data_pull_end_dir,
                            job_end_processing_dir,
                            job_end_data_put_dir
                        )
                    )
                else:
                    raise ValueError("Expected a directory to traverse")

            stats.append(exp_stats)

        return stats


    def scandir_csv(self, path):
        '''
        Recursively yield DirEntry objects for given directory.
        '''
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                continue
            else:
                yield entry


    def csv_to_dict(self, csvfile):
        '''
        Convert a csv file to dict
        '''
        mydict = {}
        with open(csvfile, mode='r') as infile:
            reader = csv.reader(infile)
            mydict = {rows[0]:float(rows[1]) for rows in reader}

        return mydict


    def update_multiple_csvs_to_dict(self, path):
        '''
        Convert multiple csv files into one dict
        '''
        dict_obj = {}
        for entry in self.scandir_csv(path):
            #### Checking if the file has the right extention
            if os.path.splitext(entry.name)[1] not in ['.csv']:
                continue
            dict_obj.update(self.csv_to_dict(entry))

        return dict_obj


    def worker_num_str_to_int(self, setup_dir_name):
        _, _, _, worker_num = setup_dir_name.split('_')
        return int(worker_num)


    def start_stats_calculation(self,
                                data_task_send_start_dir,
                                data_task_send_end_dir,
                                data_pull_start_dir,
                                data_pull_end_dir,
                                job_end_processing_dir,
                                job_end_data_put_dir):
        '''
        The main processing that does the stat calculation.
        '''

        ###########################################################
        # Reading data_send_start & data_send_end for tasks 
        ###########################################################

        data_task_send_start = self.update_multiple_csvs_to_dict(data_task_send_start_dir)
        data_task_send_end = self.update_multiple_csvs_to_dict(data_task_send_end_dir)

        print("data_task_send_start: " + str(len(data_task_send_start)))
        print("data_task_send_end: " + str(len(data_task_send_end)))

        ###########################################################
        # Reading data_pull_start, data_pull_end & job_end_data_put
        ###########################################################

        data_pull_start = self.update_multiple_csvs_to_dict(data_pull_start_dir)
        data_pull_end = self.update_multiple_csvs_to_dict(data_pull_end_dir)
        job_end_processing = self.update_multiple_csvs_to_dict(job_end_processing_dir)
        job_end_data_put = self.update_multiple_csvs_to_dict(job_end_data_put_dir)

        print("data_pull_start: " + str(len(data_pull_start)))
        print("data_pull_end: " + str(len(data_pull_end)))
        print("job_end_processing: " + str(len(job_end_processing)))
        print("job_end_data_put: " + str(len(job_end_data_put)))


        ###########################################################
        # Getting the job keys sorted by time so we can calculate
        # the stats accurately.
        ###########################################################

        d = data_pull_start
        data_pull_start_sorted = [float(d[k]) for k in sorted(d, key=d.get)]
        d = job_end_data_put
        job_end_data_put_sorted = [float(d[k]) for k in sorted(d, key=d.get)]
        job_end_data_put_sorted_pair = [(k, float(d[k])) for k in sorted(d, key=d.get)]
        d = data_task_send_end
        data_task_send_end_sorted = [float(d[k]) for k in sorted(d, key=d.get)]


        d = data_task_send_end
        data_task_send_end_sorted = [float(d[k]) for k in sorted(d, key=d.get)]

        print("======================================")
        if min(data_pull_start_sorted) > max(data_task_send_end_sorted):
            print("pre-streamed data")
        else:
            print("live-streamed data")
        print("======================================")


        #### Calculating Throughput [n(tasks)/second]

        first_job_finished_time = math.floor(job_end_data_put_sorted_pair[0][1])
        last_job_finished_time = math.floor(job_end_data_put_sorted_pair[-1][1])
        
        throughput_per_second = defaultdict(int)
        for i in range(len(job_end_data_put_sorted_pair)):
            time_step = \
                math.floor(job_end_data_put_sorted_pair[i][1]) - first_job_finished_time + 1
            throughput_per_second[time_step] += 1

        throughput_time_list = []
        throughput_job_count_list = []
        for k, v in throughput_per_second.items():
            throughput_time_list.append(k)
            throughput_job_count_list.append(v)

        norm_throughput = len(job_end_data_put_sorted_pair) / \
            (job_end_data_put_sorted_pair[-1][1] - float(data_pull_start[job_end_data_put_sorted_pair[0][0]]))

        print("len(job_end_data_put_sorted_pair):", len(job_end_data_put_sorted_pair))
        print("job_end_data_put_sorted_pair[-1][1]:", job_end_data_put_sorted_pair[-1][1])
        print("float(data_pull_start[job_end_data_put_sorted_pair[0][0]]):", float(data_pull_start[job_end_data_put_sorted_pair[0][0]]))
        print("output:", (job_end_data_put_sorted_pair[-1][1] - float(data_pull_start[job_end_data_put_sorted_pair[0][0]])))
        print("tput:", norm_throughput)

        #### Calculating Event time latency

        event_time_latency_list = []
        for key, time in job_end_data_put_sorted_pair:
            diff_value = float(job_end_data_put[key]) - float(data_task_send_end[key])
            event_time_latency_list.append(diff_value)

        return {
            "normalized_throughput": norm_throughput,
            "avg_throughput": np.mean(throughput_job_count_list),
            "std_throughput": np.std(throughput_job_count_list),
            "max_throughput": max(throughput_job_count_list),
            "all_throughput": throughput_job_count_list,
            "avg_event_time_latency": np.mean(event_time_latency_list),
            "std_event_time_latency": np.std(event_time_latency_list),
            "max_event_time_latency": max(event_time_latency_list),
            "all_event_time_latency": event_time_latency_list
        }
