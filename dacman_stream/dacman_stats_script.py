import os
import sys
import csv
import math
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt


###########################################################
# Global variables that hold latency & throughput arrays
###########################################################

event_time_latencies_arr = []
pure_process_time_latencies_arr = []
process_time_latencies_arr = []
throughput_job_count_list_arr = []
throughput_time_list_arr = []
n_jobs_arr = []
job_arrival_rate_arr = []
n_nodes_arr = []
n_processes_arr = []

###########################################################


def scandir_csv(path):
    '''
    Recursively yield DirEntry objects for given directory.
    '''
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            continue
        else:
            yield entry

def scandir_directory(path):
    '''
    Recursively yield DirEntry objects for given directory.
    '''
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield entry
        else:
            continue

def count_csv_files(path):
    '''
    Counts the number of the csv files so we can know exactly
    how many processes were running.
    '''
    i = 0
    for entry in scandir_csv(path):
        #### Checking if the file has the right extention
        if os.path.splitext(entry.name)[1] not in ['.csv']:
            continue
        i += 1

    return i

def csv_to_dict(csvfile):
    '''
    Convert a csv file to dict
    '''
    mydict = {}
    with open(csvfile, mode='r') as infile:
        reader = csv.reader(infile)
        mydict = {rows[0]:rows[1] for rows in reader}

    return mydict

def update_multiple_csvs_to_dict(path):
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

def write_dict_to_csv(dict_obj, filename, path):
    '''
    Write a dict to csv file
    '''
    full_path = os.path.join(path, filename)

    with open(full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict_obj.items():
           writer.writerow([key, value])

def aggregate_list(input_list, to_n_elements):
    '''
    Aggregate a list and break it into a list of n elements
    '''
    n_elements = len(input_list)
    n_loop = math.ceil(n_elements/to_n_elements)

    agg_list = [np.mean(input_list[i:i+n_loop]) for i in range(0, n_elements, n_loop)]

    #print("n_elements:", n_elements)
    #print("n_elements/to_n_elements:", n_elements/to_n_elements)
    #print("n_loop:", n_loop)
    #exit()

    return agg_list

def plot_latencies(dim1, dim2, figsize1, figsize2, output_dir):
    sorted_indices = [i[0] for i in sorted(enumerate(job_arrival_rate_arr),
                             key=lambda x:x[1], reverse=True)]

    #### Plotting Event-time latencies

    fig, ax = plt.subplots(dim1, dim2, sharex=True,
        figsize=(figsize1,figsize2))

    event_time_latencies_len = len(event_time_latencies_arr)

    for i in range(dim1):
        for j in range(dim2):
            k = i*dim2 + j
            if k >= event_time_latencies_len:
                break

            arr_index = sorted_indices[k]
            job_num_list = [u for u in range(1, len(event_time_latencies_arr[arr_index])+1)]

            ax_curr = ax
            if type(ax) == "numpy.ndarray":
                ax_curr = ax[i, j]

            ax_curr.plot(job_num_list, event_time_latencies_arr[arr_index])
            #ax_curr.set(title='DAR: %.1f jobs/sec' % (job_arrival_rate_arr[arr_index]))
            ax_curr.set_ylim(bottom=0)
            ax_curr.grid()
            ax_curr.set_xticklabels([])

    fig.text(0.5, 0.04, 'time', ha='center')
    fig.text(0.04, 0.5, 'Event-time latency (s)', va='center', rotation='vertical')

    title = '%i nodes, %i processes' \
            % (n_nodes_arr[0], n_processes_arr[0])

    title += ', 100% Data Size (20 MB), no bursts'

    #title += ', 100% Data Size (20 MB), no bursts\n' + \
    #         '--' + '\n' + \
    #         'DAR: Data arrival rate' \
         

    fig.suptitle(title)

    png_filename = "event_latencies_%i_%i.png" % (n_nodes_arr[0],
        n_processes_arr[0])

    fig.savefig(os.path.join(output_dir, png_filename))

    #### Plotting pure-processing-time latencies

    fig, ax = plt.subplots(dim1, dim2, sharex=True,
        figsize=(figsize1,figsize2))

    for i in range(dim1):
        for j in range(dim2):
            k = i*dim2 + j
            if k >= event_time_latencies_len:
                break

            arr_index = sorted_indices[k]
            job_num_list = [u for u in range(1, len(pure_process_time_latencies_arr[arr_index])+1)]

            ax_curr = ax
            if type(ax) == "numpy.ndarray":
                ax_curr = ax[i, j]

            ax_curr.plot(job_num_list, pure_process_time_latencies_arr[arr_index])
            #ax_curr.set(title='DAR: %.1f jobs/sec' % (job_arrival_rate_arr[arr_index]))
            ax_curr.set_ylim(bottom=0)
            ax_curr.grid()
            ax_curr.set_xticklabels([])

    fig.text(0.5, 0.04, 'time', ha='center')
    fig.text(0.04, 0.5, 'Pure-processing-time latency (s)', va='center', rotation='vertical')

    title = '%i nodes, %i processes' \
            % (n_nodes_arr[0], n_processes_arr[0])

    title += ', 100% Data Size (20 MB), no bursts'

    #title += ', 100% Data Size (20 MB), no bursts\n' + \
    #         '--' + '\n' + \
    #         'DAR: Data arrival rate' \
         

    fig.suptitle(title)

    png_filename = "pure_processing_latencies_%i_%i.png" % (n_nodes_arr[0],
        n_processes_arr[0])

    fig.savefig(os.path.join(output_dir, png_filename))

    #### Plotting Processing-time-data-put latencies

    fig, ax = plt.subplots(dim1, dim2, sharex=True,
        figsize=(figsize1,figsize2))

    for i in range(dim1):
        for j in range(dim2):
            k = i*dim2 + j
            if k >= event_time_latencies_len:
                break

            arr_index = sorted_indices[k]
            job_num_list = [u for u in range(1, len(process_time_latencies_arr[arr_index])+1)]

            ax_curr = ax
            if type(ax) == "numpy.ndarray":
                ax_curr = ax[i, j]

            ax_curr.plot(job_num_list, process_time_latencies_arr[arr_index])
            #ax_curr.set(title='DAR: %.1f jobs/sec' % (job_arrival_rate_arr[arr_index]))
            ax_curr.set_ylim(bottom=0)
            ax_curr.grid()
            ax_curr.set_xticklabels([])

    fig.text(0.5, 0.04, 'time', ha='center')
    fig.text(0.04, 0.5, 'Processing-time-data-put latency (s)', va='center', rotation='vertical')

    title = '%i nodes, %i processes' \
            % (n_nodes_arr[0], n_processes_arr[0])

    title += ', 100% Data Size (20 MB), no bursts'

    #title += ', 100% Data Size (20 MB), no bursts\n' + \
    #         '--' + '\n' + \
    #         'DAR: Data arrival rate' \
         

    fig.suptitle(title)

    png_filename = "processing_data_put_latencies_%i_%i.png" % (n_nodes_arr[0],
        n_processes_arr[0])

    fig.savefig(os.path.join(output_dir, png_filename))

    #### Plotting Throughput

    fig, ax = plt.subplots(dim1, dim2, sharex=True,
        figsize=(figsize1,figsize2))

    for i in range(dim1):
        for j in range(dim2):
            k = i*dim2 + j
            if k >= event_time_latencies_len:
                break

            arr_index = sorted_indices[k]

            ax_curr = ax
            if type(ax) == "numpy.ndarray":
                ax_curr = ax[i, j]

            ax_curr.plot(throughput_time_list_arr[arr_index],
                throughput_job_count_list_arr[arr_index])
            #ax_curr.set(title='DAR: %.1f jobs/sec' % (job_arrival_rate_arr[arr_index]))
            ax_curr.set_ylim(bottom=0)
            ax_curr.grid()

    fig.text(0.5, 0.04, 'time (s)', ha='center')
    fig.text(0.04, 0.5, 'throughput (jobs/s)', va='center', rotation='vertical')

    title = '%i nodes, %i processes' \
            % (n_nodes_arr[0], n_processes_arr[0])

    title += ', 100% Data Size (20 MB), no bursts'

    #title += ', 100% Data Size (20 MB), no bursts\n' + \
    #         '--' + '\n' + \
    #         'DAR: Data arrival rate' \
         
    fig.suptitle(title)

    png_filename = "throughputs_%i_%i.png" % (n_nodes_arr[0],
        n_processes_arr[0])

    fig.savefig(os.path.join(output_dir, png_filename))




def start_stats_calculation(data_send_start_path,
                            data_send_end_path,
                            data_pull_start_dir,
                            data_pull_end_dir,
                            job_end_processing_dir,
                            job_end_data_put_dir,
                            output_dir):
    '''
    The main processing that does the stat calculation & the 
    plotting.
    '''

    #### Creating the output file that will have the stream output
    output_filename = open(os.path.join(output_dir, "stats.txt"), 'a')

    ###########################################################
    # Reading data_send_start, data_send_end & Initial data
    ###########################################################

    data_send_start = csv_to_dict(data_send_start_path)
    data_send_end = csv_to_dict(data_send_end_path)

    ###########################################################
    # Reading data_pull_start, data_pull_end & job_end_data_put
    ###########################################################

    data_pull_start = update_multiple_csvs_to_dict(data_pull_start_dir)
    data_pull_end = update_multiple_csvs_to_dict(data_pull_end_dir)
    job_end_processing = update_multiple_csvs_to_dict(job_end_processing_dir)
    job_end_data_put = update_multiple_csvs_to_dict(job_end_data_put_dir)

    ###########################################################
    # Getting some initial stats for later calculation
    ###########################################################

    #### Getting the number of processes by counting the number
    #### of the csv files in one folder in the "finished_dir" 
    #### dir. The number of nodes n_nodes can be calculated
    #### directly bec. we were running 10 processes per node
    #### in our experiment. 
    n_processes = count_csv_files(data_pull_start_dir)
    #n_nodes = int(n_processes / 10)
    n_nodes = int(math.ceil(n_processes / 64))

    n_jobs = len(data_pull_start)

    print("====================================================",
        file=output_filename)
    print("n_nodes:", n_nodes, file=output_filename)
    print("n_processes:", n_processes, file=output_filename)
    print("n_jobs:", n_jobs, file=output_filename)
    print("====================================================",
        file=output_filename)

    ###########################################################
    # Getting the job keys sorted by time so we can calculate
    # the stats accurately.
    ###########################################################

    d = data_send_start
    keys_sorted_by_time = [(k, d[k]) for k in sorted(d, key=d.get)]
    d = job_end_data_put
    job_end_data_put_sorted = [(k, float(d[k])) for k in sorted(d, key=d.get)]

    ###########################################################
    # Calculating Stats
    ###########################################################

    #### Calculating job arrival rate [Max(data_send_end) - Min(data_send_end)]

    data_send_end_max = float('-inf')
    data_send_end_min = float('inf')
    for _, value in data_send_end.items():
           data_send_end_max = max(float(value), data_send_end_max)
           data_send_end_min = min(float(value), data_send_end_min)

    data_send_end_diff = data_send_end_max - data_send_end_min
    print("Job arrival time period [Max(Data send end) - Min(Data send end)]: ", 
        data_send_end_diff, file=output_filename)

    job_arrival_rate = float(n_jobs)/data_send_end_diff

    print("Job arrival rate [n_jobs / (data_send_end_max - data_send_end_min)]: %.1f job/s" % \
        job_arrival_rate, file=output_filename)

    #### Calculating Turnaround time [Max(Job end) - Min(Data send start)]

    job_end_data_put_max = float('-inf')
    data_send_start_min = float('inf')
    for _, value in job_end_data_put.items():
           job_end_data_put_max = max(float(value), job_end_data_put_max)
           data_send_start_min = min(float(value), data_send_start_min)

    turaround_time = job_end_data_put_max - data_send_start_min
    print("Turnaround time [Max(Job end) - Min(Data send start)]: ", 
        turaround_time, file=output_filename)

    #### Calculating pulling from Redis overhead time [Avg(Data pull end - Data pull start)]

    redis_overhead_time = []
    for key, time in keys_sorted_by_time:
        diff_value = float(data_pull_end[key]) - float(data_pull_start[key])
        redis_overhead_time.append(diff_value)

    print("Redis pull overhead time [Avg(Data pull end - Data pull start)]: ", 
        np.mean(redis_overhead_time), file=output_filename)
    #print("Redis pull overhead time: ", 
    #    redis_overhead_time, file=output_filename)

    #### Calculating Event-time Latency [Avg(Job End - Data send end)]

    latency_list = []
    for key, time in keys_sorted_by_time:
        diff_value = float(data_pull_end[key]) - float(data_send_end[key])
        latency_list.append(diff_value)

    print("Event-time Latency [Avg(Job start - Data send end)]: ", 
        np.mean(latency_list), file=output_filename)

    #### Calculating Pure Processing-time latency = 
    #### Job processing time [Avg(Job end processing - Job start)]

    pure_processing_time_latency_list = []
    for key, time in keys_sorted_by_time:
        diff_value = float(job_end_processing[key]) - float(data_pull_end[key])
        pure_processing_time_latency_list.append(diff_value)

    print("Pure-processing-time Latency [Avg(Job end processing - Job start)]: ", 
        np.mean(pure_processing_time_latency_list), file=output_filename)

    #### Calculating Processing-time-data-put Latency = 
    #### Job processing time + data put [Avg(Job end data put - Job start)]

    processing_time_latency_list = []
    for key, time in keys_sorted_by_time:
        diff_value = float(job_end_data_put[key]) - float(data_pull_end[key])
        processing_time_latency_list.append(diff_value)

    print("Processing-time-data-put Latency [Avg(Job end data put - Job start)]: ", 
        np.mean(processing_time_latency_list), file=output_filename)

    #### Calculating Throughput [n(Jobs)/Turnaround time]

    print("Throughput [n(Jobs)=%s/Turnaround time]: " % n_jobs, 
        float(n_jobs)/float(turaround_time), file=output_filename)

    #### Calculating Throughput [n(Jobs)/second]

    first_job_finished_time = math.floor(job_end_data_put_sorted[0][1])
    
    throughput_per_second = defaultdict(int)
    k = 1
    for i in range(len(job_end_data_put_sorted)):
        time_index = \
            math.floor(job_end_data_put_sorted[i][1]) - first_job_finished_time + 1

        for j in range(time_index - k):
            throughput_per_second[k+j] = 0

        k = time_index

        throughput_per_second[time_index] += 1
        k += 1

    throughput_time_list = []
    throughput_job_count_list = []
    for k, v in throughput_per_second.items():
        throughput_time_list.append(k)
        throughput_job_count_list.append(v)

    #### Calculating Data transfer overhead [Avg(Data send end - Data send start)]

    data_transfer_overhead_list = []
    for key, time in keys_sorted_by_time:
        diff_value = float(data_send_end[key]) - float(data_send_start[key])
        data_transfer_overhead_list.append(diff_value)

    data_transfer_overhead = np.mean(data_transfer_overhead_list)
    print("Data transfer overhead [Avg(Data send end - Data send start)]: ", 
        data_transfer_overhead, file=output_filename)

    #### Calculating job arrival rate [Max(data_send_end) - Min(data_send_end)]

    data_send_end_max = float('-inf')
    data_send_end_min = float('inf')
    for _, value in data_send_end.items():
           data_send_end_max = max(float(value), data_send_end_max)
           data_send_end_min = min(float(value), data_send_end_min)

    data_send_end_diff = data_send_end_max - data_send_end_min
    print("Job arrival time period [Max(Data send end) - Min(Data send end)]: ", 
        data_send_end_diff, file=output_filename)

    job_arrival_rate = float(n_jobs)/data_send_end_diff

    ###########################################################
    # Plotting
    ###########################################################

    #### Plotting Latency

    to_n_elements = 300

    #### Plotting multiple graphs in one figure
    event_time_latencies_arr.append(
            aggregate_list(latency_list, to_n_elements))
    pure_process_time_latencies_arr.append(
            aggregate_list(pure_processing_time_latency_list, to_n_elements))
    process_time_latencies_arr.append(
            aggregate_list(processing_time_latency_list, to_n_elements))
    throughput_job_count_list_arr.append(
            aggregate_list(throughput_job_count_list, to_n_elements))
    throughput_time_list_arr.append(
            aggregate_list(throughput_time_list, to_n_elements))

    n_jobs_arr.append(n_jobs)
    job_arrival_rate_arr.append(job_arrival_rate)
    n_nodes_arr.append(n_nodes)
    n_processes_arr.append(n_processes)

    '''
    #### Creates two subplots and unpacks the output array immediately
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10,10))

    ax1.plot([i for i in range(1, len(latency_list)+1)], latency_list)
    ax1.set(xlabel='job #', ylabel='Event-time latency (s)')

    ax2.plot([i for i in range(1, len(processing_time_latency_list)+1)],
        processing_time_latency_list)
    ax2.set(xlabel='job #', ylabel='Processing-time latency (s)')
    
    ax1.grid()
    ax2.grid()

    ax1.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)

    fig.suptitle('%i jobs, data arrival rate: %.1f jobs/sec, %i nodes, %i processes'\
         % (n_jobs, job_arrival_rate, n_nodes, n_processes))

    png_filename = "latency_%i_%i_%i_%.1f.png" % (n_jobs, n_nodes, n_processes, 
        job_arrival_rate)

    fig.savefig(os.path.join(output_dir, png_filename))
    #plt.show()

    #### Plotting Throughput

    fig, ax1 = plt.subplots(1, 1, sharex=True)
    ax1.plot(throughput_time_list, throughput_job_count_list)
    ax1.set(xlabel='time (s)', ylabel='throughput (jobs/s)')

    ax1.grid()

    fig.suptitle('%i jobs, data arrival rate: %.1f jobs/sec, %i nodes, %i processes'\
         % (n_jobs, job_arrival_rate, n_nodes, n_processes))

    png_filename = "throughput_%i_%i_%i_%.1f.png" % (n_jobs, n_nodes, n_processes, 
        job_arrival_rate)

    fig.savefig(os.path.join(output_dir, png_filename))
    #plt.show()

    print("====================================================",
        file=output_filename)
    '''

    output_filename.close()


def main(argv):
    ###########################################################
    # Initiating
    ###########################################################

    started_dir = os.path.abspath(sys.argv[1])
    finished_dir = os.path.abspath(sys.argv[2])
    output_dir = os.path.abspath(sys.argv[3])

    recursive_bool = bool(int(sys.argv[4]))

    if recursive_bool:
        for started_entry, finished_entry in zip(scandir_directory(started_dir),
                        scandir_directory(finished_dir)):
            if started_entry.name == finished_entry.name:
                data_send_start_path = os.path.join(started_entry, 'data_send_start.csv')
                data_send_end_path = os.path.join(started_entry, 'data_send_end.csv')

                data_pull_start_dir = os.path.join(finished_entry, "data_pull_start")
                data_pull_end_dir = os.path.join(finished_entry, "data_pull_end")
                job_end_processing_dir = os.path.join(finished_entry, "job_end_processing")
                job_end_data_put_dir = os.path.join(finished_entry, "job_end_data_put")

                start_stats_calculation(data_send_start_path,
                                        data_send_end_path,
                                        data_pull_start_dir,
                                        data_pull_end_dir,
                                        job_end_processing_dir,
                                        job_end_data_put_dir,
                                        output_dir)

        plot_latencies(2, 2, 15, 10, output_dir)
    else:
        data_send_start_path = os.path.join(started_dir, 'data_send_start.csv')
        data_send_end_path = os.path.join(started_dir, 'data_send_end.csv')

        data_pull_start_dir = os.path.join(finished_dir, "data_pull_start")
        data_pull_end_dir = os.path.join(finished_dir, "data_pull_end")
        job_end_processing_dir = os.path.join(finished_dir, "job_end_processing")
        job_end_data_put_dir = os.path.join(finished_dir, "job_end_data_put")

        start_stats_calculation(data_send_start_path,
                                data_send_end_path,
                                data_pull_start_dir,
                                data_pull_end_dir,
                                job_end_processing_dir,
                                job_end_data_put_dir,
                                output_dir)
        plot_latencies(1, 1, 8, 8, output_dir)


if __name__ == "__main__":

    if len(sys.argv) == 4:
        main(sys.argv[1:])
    elif len(sys.argv) == 5:
        main(sys.argv[1:])
    else:
        print("Usage: python dacman_stats_script.py <started_dir> <finished_dir> <output_dir> <recursive-boolean (optional)>")
        exit()

