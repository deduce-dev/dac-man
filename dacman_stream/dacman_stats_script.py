import os
import sys
import csv
import math
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt


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

def start_stats_calculation(data_send_start_path,
                            data_send_end_path,
                            data_pull_start_dir,
                            data_pull_end_dir,
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
    n_nodes = int(n_processes / 10)

    n_jobs = len(data_pull_start) + 1

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

    #### Calculating Turnaround time [Max(Job end) - Min(Data send start)]

    job_end_data_put_max = float('-inf')
    data_send_start_min = float('inf')
    for _, value in job_end_data_put.items():
           job_end_data_put_max = max(float(value), job_end_data_put_max)
           data_send_start_min = min(float(value), data_send_start_min)

    turaround_time = job_end_data_put_max - data_send_start_min
    print("Turnaround time [Max(Job end) - Min(Data send start)]: ", 
        turaround_time, file=output_filename)

    #### Calculating Event-time Latency [Avg(Job End - Data send end)]

    latency_list = []
    for key, time in keys_sorted_by_time:
        diff_value = float(data_pull_end[key]) - float(data_send_end[key])
        latency_list.append(diff_value)

    print("Event-time Latency [Avg(Job start - Data send end)]: ", 
        np.mean(latency_list), file=output_filename)

    #### Calculating Processing-time Latency = Job processing time [Avg(Job end - Job start)]

    processing_time_latency_list = []
    for key, time in keys_sorted_by_time:
        diff_value = float(job_end_data_put[key]) - float(data_pull_end[key])
        processing_time_latency_list.append(diff_value)

    print("Processing-time Latency [Avg(Job end - Job start)]: ", 
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

    ###########################################################
    # Plotting
    ###########################################################

    #### Plotting Latency

    #### Creates two subplots and unpacks the output array immediately
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10,10))

    ax1.plot([i for i in range(1, len(latency_list)+1)], latency_list)
    ax1.set(xlabel='jobs', ylabel='Event-time latency (s)')

    ax2.plot([i for i in range(1, len(processing_time_latency_list)+1)],
        processing_time_latency_list)
    ax2.set(xlabel='jobs', ylabel='Processing-time latency (s)')
    
    ax1.grid()
    ax2.grid()

    fig.suptitle('%i jobs, data generation rate: %.1f jobs/sec, %i nodes, %i processes'\
         % (n_jobs, 1.0/data_transfer_overhead, n_nodes, n_processes))

    png_filename = "latency_%i_%i_%i_%.1f.png" % (n_jobs, n_nodes, n_processes, 
        1.0/data_transfer_overhead)

    fig.savefig(os.path.join(output_dir, png_filename))
    #plt.show()

    #### Plotting Throughput

    fig, ax1 = plt.subplots(1, 1, sharex=True)
    ax1.plot(throughput_time_list, throughput_job_count_list)
    ax1.set(xlabel='time (s)', ylabel='throughput (jobs/s)')

    ax1.grid()

    fig.suptitle('%i jobs, data generation rate: %.1f jobs/sec, %i nodes, %i processes'\
         % (n_jobs, 1.0/data_transfer_overhead, n_nodes, n_processes))

    png_filename = "throughput_%i_%i_%i_%.1f.png" % (n_jobs, n_nodes, n_processes, 
        1.0/data_transfer_overhead)

    fig.savefig(os.path.join(output_dir, png_filename))
    #plt.show()

    print("====================================================",
        file=output_filename)

    output_filename.close()


def main(argv):
    ###########################################################
    # Initiating
    ###########################################################

    started_dir = os.path.abspath(sys.argv[1])
    finished_dir = os.path.abspath(sys.argv[2])
    output_dir = os.path.abspath(sys.argv[3])

    recursive_bool = bool(sys.argv[3])

    if recursive_bool:
        for started_entry, finished_entry in zip(scandir_directory(started_dir),
                        scandir_directory(finished_dir)):
            if started_entry.name == finished_entry.name:
                data_send_start_path = os.path.join(started_entry, 'data_send_start.csv')
                data_send_end_path = os.path.join(started_entry, 'data_send_end.csv')

                data_pull_start_dir = os.path.join(finished_entry, "data_pull_start")
                data_pull_end_dir = os.path.join(finished_entry, "data_pull_end")
                job_end_data_put_dir = os.path.join(finished_entry, "job_end_data_put")

                start_stats_calculation(data_send_start_path,
                                        data_send_end_path,
                                        data_pull_start_dir,
                                        data_pull_end_dir,
                                        job_end_data_put_dir,
                                        output_dir)
    else:
        data_send_start_path = os.path.join(started_dir, 'data_send_start.csv')
        data_send_end_path = os.path.join(started_dir, 'data_send_end.csv')

        data_pull_start_dir = os.path.join(finished_dir, "data_pull_start")
        data_pull_end_dir = os.path.join(finished_dir, "data_pull_end")
        job_end_data_put_dir = os.path.join(finished_dir, "job_end_data_put")

        start_stats_calculation(data_send_start_path,
                                data_send_end_path,
                                data_pull_start_dir,
                                data_pull_end_dir,
                                job_end_data_put_dir,
                                output_dir)


if __name__ == "__main__":

    if len(sys.argv) == 4:
        main(sys.argv[1:])
    elif len(sys.argv) == 5:
        main(sys.argv[1:])
    else:
        print("Usage: python dacman_stats_script.py <start_dir> <finished_dir> <output_dir> <recursive-boolean (optional)>")
        exit()

