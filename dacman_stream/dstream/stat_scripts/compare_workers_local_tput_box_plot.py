import os
import sys
import csv
import math
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

font = {
    'size': 28,
}
font_bar_t = {
    'size': 18,
}
label_size = 28
legend_size = 20
label_pad_y = 15
label_pad_x = 10
figsize1 = 9
figsize2 = 5
graph_ext = "pdf"
#graph_ext = "png"

is_log = False

sources_dir_name = "sources"
workers_dir_name = "workers"

tput_arrays_local = []
tput_arrays_cluster = []

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

def plot_box_plots(figsize1, figsize2, xticks_labels, output_dir):
    N = len(tput_arrays_local)

    ind = np.arange(N)    # the x locations for the groups
    width = 0.25         # the width of the bars

    fig, ax = plt.subplots(figsize=(figsize1,figsize2))

    c = 'b'
    p1 = ax.boxplot(tput_arrays_local, positions=ind, patch_artist=True, widths=width,
            boxprops=dict(facecolor=c, color=c))
    c = 'r'
    p2 = ax.boxplot(tput_arrays_cluster, positions=(ind+width), patch_artist=True, widths=width,
            boxprops=dict(facecolor=c, color=c))

    ax.set_xticks(ind + width / 2)

    ax.set_xticklabels(('1', '4', '8', '16', '32', '64'))
    ax.tick_params(labelsize=label_size)

    ax.set_ylabel("Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
    ax.set_xlabel("Number of Workers", fontdict=font, labelpad=label_pad_x)

    ax.legend((p1["boxes"][0], p2["boxes"][0]), ('Local', 'Cluster'), fontsize=legend_size, ncol=2, loc="upper left")
    #ax.set_yscale('log')

    #fig.canvas.draw()
    #ax.relim()
    ax.autoscale_view()
    ax.set_ylim(top=750)
    plt.tight_layout()

    graph_filename = "tput_buffered_stream_box_plot." + graph_ext
    plt.savefig(os.path.join(output_dir, graph_filename))

def start_stats_calculation(data_pull_start_dir,
                            data_pull_end_dir,
                            job_end_processing_dir,
                            job_end_data_put_dir,
                            setup_name):
    '''
    The main processing that does the stat calculation & the 
    plotting.
    '''
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

    d = job_end_data_put
    job_end_data_put_sorted = [float(d[k]) for k in sorted(d, key=d.get)]
    job_end_data_put_sorted_pair = [(k, float(d[k])) for k in sorted(d, key=d.get)]

    #### Calculating Throughput [n(tasks)/second]

    first_job_finished_time = math.floor(job_end_data_put_sorted_pair[0][1])
    
    throughput_per_second = defaultdict(int)
    for i in range(len(job_end_data_put_sorted_pair)):
        time_step = \
            math.floor(job_end_data_put_sorted_pair[i][1]) - first_job_finished_time + 1
        throughput_per_second[time_step] += 1

    throughput_job_count_list = []
    for k, v in throughput_per_second.items():
        throughput_job_count_list.append(v)

    return throughput_job_count_list


def process_data(experiment_dir, setup_names):
    all_arrays = []
    for setup_n in setup_names:
        print("setup_name:", setup_n)
        current_dir = os.path.join(experiment_dir, setup_n)
        sources_dir = os.path.join(current_dir, sources_dir_name)
        workers_dir = os.path.join(current_dir, workers_dir_name)
        #workers_dir = current_dir

        data_pull_start_dir = os.path.join(workers_dir, "data_pull_start")
        data_pull_end_dir = os.path.join(workers_dir, "data_pull_end")
        job_end_processing_dir = os.path.join(workers_dir, "job_end_processing")
        job_end_data_put_dir = os.path.join(workers_dir, "job_end_data_put")

        all_arrays.append(start_stats_calculation(
            data_pull_start_dir,
            data_pull_end_dir,
            job_end_processing_dir,
            job_end_data_put_dir,
            setup_n))

    print("setup_names:", str(setup_names))
    return all_arrays

def main(argv):
    global tput_arrays_local
    global tput_arrays_cluster

    local_experiment_dir = os.path.abspath(argv[0])
    cluster_experiment_dir = os.path.abspath(argv[1])
    output_dir = os.path.abspath(argv[2])

    setup_names = []

    for entry in os.scandir(local_experiment_dir):
        if entry.is_dir(follow_symlinks=False):
            setup_names.append(entry.name)

    xticks_labels = []
    if setup_names:
        setup_names = sorted(setup_names,
            key=lambda v: worker_num_str_to_int(v))
        #xticks_labels = ['_'.join(x.split('_')[2:]) for x in setup_names]
        xticks_labels = [x.split('_')[3] for x in setup_names]

    tput_arrays_local = process_data(local_experiment_dir, setup_names)
    tput_arrays_cluster = process_data(cluster_experiment_dir, setup_names)

    plot_box_plots(9, 5, xticks_labels, output_dir)

if __name__ == "__main__":

    if len(sys.argv) == 4:
        main(sys.argv[1:])
    else:
        print("Usage: python compare_workers_local_tput_box_plot.py <local_experiment_dir> <cluster_experiment_dir> <output_dir>")
        exit()


