
import settings as _settings

class StatGenerator(object):
    def __init__(self):
        self._sources_dir_name = "sources"
        self._workers_dir_name = "workers"

        self._setup_names = []
        self._norm_throughput_live_vals = []
        self._norm_throughput_buffered_vals = []
        self._avg_throughput_vals = []
        self._max_throughput_vals = []
        self._std_throughput_vals = []

        self._avg_event_time_latency_vals = []
        self._max_event_time_latency_vals = []
        self._std_event_time_latency_vals = []

        # this calculates the time from where workers started to pull tasks
        # job_data_put_end - data_pull_start
        self._total_exp_time_vals = []

        # this calculates the time from where workers started to pull tasks
        # job_data_put_end - data_task_send_end
        self._runtime_vals = []

        self._pure_processing_time_vals = []

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
        for entry in scandir_csv(path):
            #### Checking if the file has the right extention
            if os.path.splitext(entry.name)[1] not in ['.csv']:
                continue
            dict_obj.update(csv_to_dict(entry))

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
        The main processing that does the stat calculation & the 
        plotting.
        '''

        ###########################################################
        # Reading data_send_start & data_send_end for tasks 
        ###########################################################

        data_task_send_start = update_multiple_csvs_to_dict(data_task_send_start_dir)
        data_task_send_end = update_multiple_csvs_to_dict(data_task_send_end_dir)

        print("data_task_send_start: " + str(len(data_task_send_start)))
        print("data_task_send_end: " + str(len(data_task_send_end)))

        ###########################################################
        # Reading data_pull_start, data_pull_end & job_end_data_put
        ###########################################################

        data_pull_start = update_multiple_csvs_to_dict(data_pull_start_dir)
        data_pull_end = update_multiple_csvs_to_dict(data_pull_end_dir)
        job_end_processing = update_multiple_csvs_to_dict(job_end_processing_dir)
        job_end_data_put = update_multiple_csvs_to_dict(job_end_data_put_dir)

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

        norm_throughput_live = len(job_end_data_put_sorted_pair) / \
            (job_end_data_put_sorted_pair[-1][1] - float(data_pull_start[job_end_data_put_sorted_pair[0][0]]))

        norm_throughput_buffered = len(job_end_data_put_sorted_pair) / \
            (job_end_data_put_sorted_pair[-1][1] - job_end_data_put_sorted_pair[0][1])

        #### Calculating Event time latency

        event_time_latency_list = []
        for key, time in job_end_data_put_sorted_pair:
            diff_value = float(job_end_data_put[key]) - float(data_task_send_end[key])
            event_time_latency_list.append(diff_value)

        print("latency: min =", min(event_time_latency_list), ", max =", max(event_time_latency_list))

        #### Calculating Pure Processing-time latency = 
        #### Job processing time [Avg(Job end processing - Job start)]

        pure_processing_time_latency_list = []
        for key, time in job_end_data_put_sorted_pair:
            diff_value = float(job_end_processing[key]) - float(data_pull_end[key])
            pure_processing_time_latency_list.append(diff_value)

        norm_throughput_live_vals.append(norm_throughput_live)
        norm_throughput_buffered_vals.append(norm_throughput_buffered)
        avg_throughput_vals.append(np.mean(throughput_job_count_list))
        std_throughput_vals.append(np.std(throughput_job_count_list))
        max_throughput_vals.append(max(throughput_job_count_list))
        avg_event_time_latency_vals.append(np.mean(event_time_latency_list))
        std_event_time_latency_vals.append(np.std(event_time_latency_list))
        max_event_time_latency_vals.append(max(event_time_latency_list))
        total_exp_time_vals.append(max(job_end_data_put_sorted) - min(data_pull_start_sorted))
        runtime_vals.append(max(job_end_data_put_sorted) - min(data_task_send_end_sorted))
        pure_processing_time_vals.append(np.mean(pure_processing_time_latency_list))