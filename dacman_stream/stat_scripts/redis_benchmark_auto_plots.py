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
    payload_size = ' '.join([f_info[-2], f_info[-1].split('.')[0].upper()])

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

def payload_size_to_int(payload_size_str):
    byte_sizes = ['B', 'KB', 'MB', 'GB']

    byte_sizes_dict = {}
    for i, b_s in enumerate(byte_sizes):
        byte_sizes_dict[b_s] = 10**(i*3)

    payload_num, payload_unit_num = \
        payload_size_str.split()

    return int(payload_num) * byte_sizes_dict[payload_unit_num]


def get_sorted_mean_std_arrs(avg_cmd_dict, std_cmd_dict):

    first_cmd = list(avg_cmd_dict.keys())[0]
    #print(avg_cmd_dict.items())

    sorted_size_pair = sorted(avg_cmd_dict[first_cmd].items(), 
        key=lambda kv: payload_size_to_int(kv[0]))
    #print(sorted_size_pair)

    sorted_size_keys = [k for k,_ in sorted_size_pair]
    #print(sorted_size_keys)
    #print(avg_cmd_dict[first_cmd][sorted_size_keys[0]])
    
    avg_dict = defaultdict(list)
    std_dict = defaultdict(list)

    for cmd, _ in avg_cmd_dict.items():
        for size_key in sorted_size_keys:
            avg_dict[cmd].append(avg_cmd_dict[cmd][size_key])
            std_dict[cmd].append(std_cmd_dict[cmd][size_key])

    return avg_dict, std_dict, sorted_size_keys

def plot_r_benchmarks(n_cli, n_reqs,
                    avg_cmd_dict, std_cmd_dict,
                    ticks_labels, filename, csv_dir):
    width = 0.35

    plt.figure(figsize=(10,7))

    i = 0
    for cmd, avg_val_arr in avg_cmd_dict.items():
        avg_val_arr = avg_cmd_dict[cmd]
        std_val_arr = std_cmd_dict[cmd]
        
        n_vars = len(avg_val_arr)

        assert n_vars == len(std_val_arr), "number of vars must be equal to data length"

        ind = np.arange(n_vars)

        plt.bar(ind + i*width, avg_val_arr, width, yerr=std_val_arr,
            label=cmd)
        i += 1

    plt.ylabel('requests/s')

    plt.xticks(ind + (i-1)*width/2, ticks_labels)
    #plt.xticks(ind, ticks_labels)
    plt.legend(loc='best')

    plt.title("redis-benchmark (%s client & %s requests)" % \
        (n_cli, n_reqs))
    #plt.show()

    plots_dir = filename.split('/')[0]

    plots_full_path = os.path.join(csv_dir, plots_dir)
    if not os.path.exists(plots_full_path):
        os.makedirs(plots_full_path)

    print(os.path.join(csv_dir, filename))
    plt.savefig(os.path.join(csv_dir, filename))


def s_main(args):
    csv_dir = args['csv_dir']
    stop_at = int(args['stop_at'])

    avg_cmd_dict = defaultdict(lambda: defaultdict(float))
    std_cmd_dict = defaultdict(lambda: defaultdict(float))

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

        new_arr = csv_to_arr(entry, stop_at)

        #avg_cmd_dict[cmd][payload_size].append(np.mean(new_arr))
        #std_cmd_dict[cmd][payload_size].append(np.std(new_arr))

        avg_cmd_dict[cmd][payload_size] = np.mean(new_arr)
        std_cmd_dict[cmd][payload_size] = np.std(new_arr)
    
    plot_filename = "plots/redis_benchmark_plot_n_%s_%s.png" % (str(n_cli), str(n_reqs))

    avg_cmd_dict, std_cmd_dict, ticks_labels = get_sorted_mean_std_arrs(avg_cmd_dict, std_cmd_dict)

    plot_r_benchmarks(n_cli, n_reqs,
        avg_cmd_dict, std_cmd_dict,
        ticks_labels, plot_filename, csv_dir)


if __name__ == '__main__':
    if (len(sys.argv) < 3):
            print("Usage: python redis_benchmark_auto_plots.py <csv_dir> <stop_at>")
    else:
        args = {
            'csv_dir': sys.argv[1],
            'stop_at': sys.argv[2]
        }
        s_main(args)