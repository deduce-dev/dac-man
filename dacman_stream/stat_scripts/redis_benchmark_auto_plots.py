import os
import sys
import csv
from collections import defaultdict 
import numpy as np
import matplotlib.pyplot as plt


def get_filename_info(filename):
    # example format: set_get_c_1_n_1_20_mb.csv

    f_info = filename.split('_')

    cmd = '_'.join(f_info[:-6])
    n_cli = f_info[-5]
    n_reqs = f_info[-3]
    payload_size = f_info[-2] + f_info[-1].split('.')[0].upper()

    return cmd, n_cli, n_reqs, payload_size

def scandir_csv(path):
    '''
    Recursively yield entry objects for given directory.
    '''
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            continue
        else:
            yield entry

def csv_to_arr(csvfile, stop_at):
    '''
    Convert a csv file to dict
    '''
    myarr = []
    with open(csvfile, mode='r') as infile:
        reader = csv.reader(infile)
        for i, row in enumerate(reader):
            if i >= stop_at:
                break
            myarr.append(float(row[1]))

    return myarr

def plot_r_benchmarks(n_cli, n_reqs,
                    avg_cmd_dict, std_cmd_dict,
                    ticks_labels, filename):
    width = 0.35

    plt.figure(figsize=(10,7))

    i = 0
    for cmd, avg_val_arr in avg_cmd_dict.items():
        std_val_arr = std_cmd_dict[cmd]
        
        n_vars = len(avg_val_arr)

        assert n_vars == len(std_val_arr), "number of vars must be equal to data length"

        ind = np.arange(n_vars)

        plt.bar(ind + i*width, avg_val_arr, width, yerr=std_val_arr,
            label=cmd)
        i += 1

    plt.ylabel('requests/s')

    plt.xticks(ind + i*width/2, ticks_labels)
    plt.legend(loc='best')

    plt.title("redis-benchmark (%s client & %s requests)" % \
        (n_cli, n_reqs))
    #plt.show()

    plt.savefig(filename)


def s_main(args):
    csv_dir = args['csv_dir']
    stop_at = int(args['stop_at'])

    avg_cmd_dict = defaultdict(list)
    std_cmd_dict = defaultdict(list)

    payload_sizes = []

    n_cli = None
    n_reqs = None
    first_loop = True

    for entry in scandir_csv(csv_dir):
        cmd, n_cli_temp, n_reqs_temp, payload_size = get_filename_info(entry.name)

        if first_loop:
            n_cli = n_cli_temp
        elif n_cli != n_cli_temp:
            print("Number of clients don't match")
            sys.exit()
        
        if first_loop:
            n_reqs = n_reqs_temp
        elif n_reqs != n_reqs_temp:
            print("Number of requests don't match")
            sys.exit()
        
        first_loop = False

        if payload_size not in payload_sizes:
            payload_sizes.append(payload_size)

        new_arr = csv_to_arr(entry, stop_at)

        avg_cmd_dict[cmd].append(np.mean(new_arr))
        std_cmd_dict[cmd].append(np.std(new_arr))
    
    plot_filename = "redis_benchmark_plot_n_%s_%s" % (str(n_cli), str(n_reqs))

    plot_r_benchmarks(n_cli, n_reqs,
        avg_cmd_dict, std_cmd_dict, payload_sizes, plot_filename)


if __name__ == '__main__':
    if (len(sys.argv) < 3):
            print("Usage: python redis_benchmark_auto_plots.py <csv_dir> <stop_at>")
    else:
        args = {
            'csv_dir': sys.argv[1],
            'stop_at': sys.argv[2]
        }
        s_main(args)