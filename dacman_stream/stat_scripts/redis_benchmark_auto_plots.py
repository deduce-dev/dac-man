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
    n_cli = int(f_info[-5])
    n_reqs = int(f_info[-3])
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
            if entry.name == ".DS_Store":
                continue
            yield entry

def csv_to_dict(csvfile, stop_at):
    '''
    Convert a csv file to dict
    '''
    mydict = defaultdict(list)
    with open(csvfile, mode='r') as infile:
        reader = csv.reader(infile)
        for i, row in enumerate(reader):
            if i >= stop_at:
                break
            mydict[row[0]].append(float(row[1]))

    return mydict

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

    sorted_size_pair = sorted(avg_cmd_dict[first_cmd].items(), 
        key=lambda kv: payload_size_to_int(kv[0]))

    sorted_size_keys = [k for k,_ in sorted_size_pair]
    
    avg_dict = defaultdict(list)
    std_dict = defaultdict(list)

    for cmd, _ in avg_cmd_dict.items():
        for size_key in sorted_size_keys:
            avg_dict[cmd].append(avg_cmd_dict[cmd][size_key])
            std_dict[cmd].append(std_cmd_dict[cmd][size_key])

    return avg_dict, std_dict, sorted_size_keys

def get_sorted_clients(avg_clients_dict, std_clients_dict):

    sorted_avg_pair = sorted(avg_clients_dict.items(), 
        key=lambda kv: int(kv[0].split('_')[1]))
    sorted_std_pair = sorted(std_clients_dict.items(), 
        key=lambda kv: int(kv[0].split('_')[1]))

    sorted_size_keys = [k for k,_ in sorted_avg_pair]

    return sorted_avg_pair, sorted_std_pair, sorted_size_keys

def plot_cmds(n_cli, n_reqs,
                avg_cmd_dict, std_cmd_dict,
                ticks_labels, filename, csv_dir):
    cmd_list = ["SET", "GET", "RPUSH", "LPUSH"]
    cmd_color_dict = {
        "SET": 'b',
        "GET": '#FF9C00',
        "RPUSH": 'g',
        "LPUSH": 'y'
    }

    width = 0.35

    plt.figure(figsize=(10,7))

    i = 0
    #for cmd, avg_val_arr in avg_cmd_dict.items():
    for cmd in cmd_list:
        if not avg_cmd_dict[cmd]:
            continue

        avg_val_arr = avg_cmd_dict[cmd]
        std_val_arr = std_cmd_dict[cmd]
        
        n_vars = len(avg_val_arr)

        assert n_vars == len(std_val_arr), "number of vars must be equal to data length"

        ind = np.arange(n_vars)

        plt.bar(ind + i*width, avg_val_arr, width, yerr=std_val_arr,
            label=cmd, color=cmd_color_dict[cmd])
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


def plot_clients(n_cli, n_reqs,
                avg_clients_cmds,
                clients_labels, ticks_labels,
                filename, clients_dir):

    cmd_list = ["SET", "GET", "RPUSH", "LPUSH"]
    cmd_color_dict = {
        "SET": 'b',
        "GET": '#FF9C00',
        "RPUSH": 'g',
        "LPUSH": 'y'
    }

    width = 0.35

    dim_1 = 1
    dim_2 = 2
    fig, ax = plt.subplots(dim_1, dim_2, #sharex=True,
        figsize=(10,7))

    for i, cmd in enumerate(cmd_list):
        if i >= dim_1*dim_2:
            break
        for client_key, cmds_dict in avg_clients_cmds:
            avg_cmd_val_arr = cmds_dict[cmd]
            
            n_vars = len(avg_cmd_val_arr) + 1
            x_ticks = np.arange(1, n_vars)

            ax_curr = ax[i]
            ax_curr.plot(x_ticks, avg_cmd_val_arr, label=client_key)

            ax_curr.set_xticks(x_ticks)
            ax_curr.set_xticklabels(ticks_labels)

            ax_curr.legend(loc='best')
    
            ax_curr.set_title(cmd)

    fig.suptitle("%s requests" % (n_reqs))

    fig.text(0.5, 0.04, 'data sizes', ha='center')
    fig.text(0.04, 0.5, 'requests/s', va='center', rotation='vertical')

    plots_dir = filename.split('/')[0]

    plots_full_path = os.path.join(clients_dir, plots_dir)
    if not os.path.exists(plots_full_path):
        os.makedirs(plots_full_path)

    fig.savefig(os.path.join(clients_dir, filename))


def compare_cmds(csv_dir, stop_at, do_plot=True):
    avg_cmd_dict = defaultdict(lambda: defaultdict(float))
    std_cmd_dict = defaultdict(lambda: defaultdict(float))

    n_cli = None
    n_reqs = None
    first_loop = True

    for entry in scandir_csv(csv_dir):
        _, n_cli_temp, n_reqs_temp, payload_size = get_filename_info(entry.name)

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

        pure_cmd_dict = csv_to_dict(entry, stop_at)

        #avg_cmd_dict[cmd][payload_size].append(np.mean(new_arr))
        #std_cmd_dict[cmd][payload_size].append(np.std(new_arr))

        for cmd, req_rate_arr in pure_cmd_dict.items():
            avg_cmd_dict[cmd][payload_size] = np.mean(req_rate_arr)
            std_cmd_dict[cmd][payload_size] = np.std(req_rate_arr)

    avg_cmd_dict, std_cmd_dict, ticks_labels = get_sorted_mean_std_arrs(avg_cmd_dict, std_cmd_dict)

    plot_filename = "plots/cmds_rb_plot_c_%d_n_%d_d_%d.png" % \
         (n_cli, n_reqs, len(ticks_labels))

    if do_plot:
        print("plotting")
        plot_cmds(n_cli, n_reqs,
            avg_cmd_dict, std_cmd_dict,
            ticks_labels, plot_filename, csv_dir)

    return n_cli, n_reqs, avg_cmd_dict, std_cmd_dict, ticks_labels

def compare_clients_num(clients_dir, stop_at):

    avg_clients_dict = defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(float)
                        )
                    )
    std_clients_dict = defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(float)
                        )
                    )

    n_cli = None
    n_reqs = None
    ticks_labels = []

    for entry in os.scandir(clients_dir):
        if entry.is_dir(follow_symlinks=False):
            if entry.name in ["temp", "plots"]:
                continue
            n_cli, n_reqs, avg_cmd_dict, std_cmd_dict, ticks_labels = \
                compare_cmds(entry, stop_at, do_plot=True)

            client_key = "c_" + str(n_cli)
            avg_clients_dict[client_key] = avg_cmd_dict
            std_clients_dict[client_key] = std_cmd_dict

    avg_clients_cmds, std_clients_cmds, clients_labels = \
        get_sorted_clients(avg_clients_dict, std_clients_dict)

    plot_filename = "plots/clients_rb_plot_c_%d_n_%d_d_%d.png" % \
         (n_cli, n_reqs, len(ticks_labels))

    plot_clients(n_cli, n_reqs,
        avg_clients_cmds,
        clients_labels, ticks_labels,
        plot_filename, clients_dir)


def s_main(args):
    csv_dir = args['csv_dir']
    stop_at = int(args['stop_at'])
    analysis_type = int(args['analysis_type'])

    if analysis_type == 1:
        compare_cmds(csv_dir, stop_at)
    elif analysis_type == 2:
        compare_clients_num(csv_dir, stop_at)


if __name__ == '__main__':
    if (len(sys.argv) < 4):
            print("Usage: python redis_benchmark_auto_plots.py <csv_dir> <stop_at> <analysis_type>")
    else:
        args = {
            'csv_dir': sys.argv[1],
            'stop_at': sys.argv[2],
            'analysis_type': sys.argv[3]
        }
        s_main(args)
