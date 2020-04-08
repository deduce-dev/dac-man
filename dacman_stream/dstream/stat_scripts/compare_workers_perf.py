import os
import sys
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

sources_dir_name = "sources"
workers_dir_name = "workers"

setup_names = []
norm_throughput_live_vals = []
norm_throughput_buffered_vals = []
avg_throughput_vals = []
max_throughput_vals = []
std_throughput_vals = []

avg_event_time_latency_vals = []
max_event_time_latency_vals = []
std_event_time_latency_vals = []

# this calculates the time from where workers started to pull tasks
# job_data_put_end - data_pull_start
total_exp_time_vals = []

# this calculates the time from where workers started to pull tasks
# job_data_put_end - data_task_send_end
runtime_vals = []

pure_processing_time_vals = []


def scandir_csv(path):
    '''
    Recursively yield DirEntry objects for given directory.
    '''
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            continue
        else:
            yield entry

def csv_to_dict(csvfile):
    '''
    Convert a csv file to dict
    '''
    mydict = {}
    with open(csvfile, mode='r') as infile:
        reader = csv.reader(infile)
        mydict = {rows[0]:float(rows[1]) for rows in reader}

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

def worker_num_str_to_int(setup_dir_name):
    _, _, _, worker_num = setup_dir_name.split('_')
    return int(worker_num)

def plot_worker_performances(figsize1, figsize2, xticks_labels, output_dir):

    font = {
        'size': 28,
    }
    label_size = 28
    label_pad_y = 15
    label_pad_x = 10
    graph_ext = "pdf"
    #graph_ext = "png"

    ########################################################
    #### Plotting average throughput between setups
    ########################################################

    plt.figure(figsize=(figsize1,figsize2))
    
    y_pos = np.arange(len(setup_names))

    #plt.bar(y_pos, avg_throughput_vals, color='b')
    plt.plot(y_pos, avg_throughput_vals, '--bo')
    
    #plt.ylim(bottom=0, top=10000)
    plt.ylim(bottom=0)
    #plt.grid()
    plt.xticks(y_pos, xticks_labels)
    plt.tick_params(labelsize=label_size)
    #plt.ylabel("Avg Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
    plt.ylabel("Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
    plt.xlabel("Number of Workers", fontdict=font, labelpad=label_pad_x)
    plt.tight_layout()
    #plt.title()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #graph_filename = "avg_throughput." + graph_ext
    graph_filename = "avg_tput." + graph_ext
    plt.savefig(os.path.join(output_dir, graph_filename))

    plt.clf()

    ########################################################
    #### Plotting maximum throughput between setups
    ########################################################

    plt.figure(figsize=(figsize1,figsize2))

    plt.bar(y_pos, max_throughput_vals)
    
    plt.ylim(bottom=0)
    #plt.grid()
    plt.xticks(y_pos, xticks_labels)
    plt.tick_params(labelsize=label_size)
    plt.ylabel("Max Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
    plt.xlabel("Number of Workers", fontdict=font, labelpad=label_pad_x)
    plt.tight_layout()
    #plt.title()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #graph_filename = "max_throughput." + graph_ext
    graph_filename = "max_tput." + graph_ext
    plt.savefig(os.path.join(output_dir, graph_filename))

    plt.clf()

    ########################################################
    #### Plotting time taken to process all tasks already in
    #### Queue
    ########################################################

    plt.figure(figsize=(figsize1,figsize2))

    plt.bar(y_pos, total_exp_time_vals)
    
    plt.ylim(bottom=0)
    #plt.grid()
    plt.xticks(y_pos, xticks_labels)
    plt.tick_params(labelsize=label_size)
    plt.ylabel("Total Runtime (s)", fontdict=font, labelpad=label_pad_y)
    plt.xlabel("Number of Workers", fontdict=font, labelpad=label_pad_x)
    plt.tight_layout()
    #plt.title()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #graph_filename = "time_all_tasks." + graph_ext
    graph_filename = "scalability." + graph_ext
    plt.savefig(os.path.join(output_dir, graph_filename))

    plt.clf()

    ########################################################
    #### Plotting average time taken to process single job 
    #### on cpu. pure-processing time
    ########################################################

    plt.figure(figsize=(figsize1,figsize2))

    plt.bar(y_pos, pure_processing_time_vals)
    
    plt.ylim(bottom=0)
    #plt.grid()
    plt.xticks(y_pos, xticks_labels)
    plt.tick_params(labelsize=label_size)
    plt.ylabel("Avg single task CPU Runtime (s)", fontdict=font, labelpad=label_pad_y)
    plt.xlabel("Number of Workers", fontdict=font, labelpad=label_pad_x)
    plt.tight_layout()
    #plt.rcParams["font.family"] = "Times New Roman"
    #plt.rcParams["font.size"] = "50"
    #plt.title()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    graph_filename = "cpu_processing_time_runtime." + graph_ext
    plt.savefig(os.path.join(output_dir, graph_filename))

    plt.clf()


    
def start_stats_calculation(data_datablock_send_start_dir,
                            data_datablock_send_end_dir,
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
    # Reading data_send_start & data_send_end for tasks &
    # datablocks
    ###########################################################

    #data_datablock_send_start = update_multiple_csvs_to_dict(data_datablock_send_start_dir)
    #data_datablock_send_end = update_multiple_csvs_to_dict(data_datablock_send_end_dir)
    data_task_send_start = update_multiple_csvs_to_dict(data_task_send_start_dir)
    data_task_send_end = update_multiple_csvs_to_dict(data_task_send_end_dir)

    #print("data_datablock_send_start: " + str(len(data_datablock_send_start)))
    #print("data_datablock_send_end: " + str(len(data_datablock_send_end)))
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


def main(argv):
    global setup_names

    experiment_dir = os.path.abspath(argv[0])
    output_dir = os.path.abspath(argv[1])

    for entry in os.scandir(experiment_dir):
        if entry.is_dir(follow_symlinks=False):
            setup_names.append(entry.name)

    xticks_labels = []
    if setup_names:
        setup_names = sorted(setup_names,
            key=lambda v: worker_num_str_to_int(v))
        #xticks_labels = ['_'.join(x.split('_')[2:]) for x in setup_names]
        xticks_labels = [x.split('_')[3] for x in setup_names]

    for setup_n in setup_names:
        print("setup_name:", setup_n)
        current_dir = os.path.join(experiment_dir, setup_n)
        sources_dir = os.path.join(current_dir, sources_dir_name)
        workers_dir = os.path.join(current_dir, workers_dir_name)
        #workers_dir = current_dir

        data_datablock_send_start_dir = os.path.join(sources_dir, "data_datablock_send_start")
        data_datablock_send_end_dir = os.path.join(sources_dir, "data_datablock_send_end")
        data_task_send_start_dir = os.path.join(sources_dir, "data_task_send_start")
        data_task_send_end_dir = os.path.join(sources_dir, "data_task_send_end")

        data_pull_start_dir = os.path.join(workers_dir, "data_pull_start")
        data_pull_end_dir = os.path.join(workers_dir, "data_pull_end")
        job_end_processing_dir = os.path.join(workers_dir, "job_end_processing")
        job_end_data_put_dir = os.path.join(workers_dir, "job_end_data_put")

        start_stats_calculation(
            data_datablock_send_start_dir,
            data_datablock_send_end_dir,
            data_task_send_start_dir,
            data_task_send_end_dir,
            data_pull_start_dir,
            data_pull_end_dir,
            job_end_processing_dir,
            job_end_data_put_dir)

    print("setup_names:", str(setup_names))
    print("norm_throughput_live_vals:", str(norm_throughput_live_vals))
    print("norm_throughput_buffered_vals:", str(norm_throughput_buffered_vals))
    print("avg_throughput_vals:", str(avg_throughput_vals))
    print("std_throughput_vals:", str(std_throughput_vals))
    print("max_throughput_vals:", str(max_throughput_vals))
    print("avg_event_time_latency_vals:", str(avg_event_time_latency_vals))
    print("std_event_time_latency_vals:", str(std_event_time_latency_vals))
    print("max_event_time_latency_vals:", str(max_event_time_latency_vals))
    print("total_exp_time_vals:", str(total_exp_time_vals))
    print("runtime_vals:", str(runtime_vals))

    plot_worker_performances(9, 5, xticks_labels, output_dir)

if __name__ == "__main__":

    if len(sys.argv) == 3:
        main(sys.argv[1:])
    else:
        print("Usage: python compare_workers.py <experiment_dir> <output_dir>")
        exit()

