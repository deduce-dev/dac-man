import os
import sys
import csv
from collections import defaultdict 
import numpy as np
import matplotlib.pyplot as plt


graph_ext = "pdf"
#graph_ext = "png"

def get_filename_info(filename):
    # example format: set_get_c_1_n_1_20_mb.csv

    f_info = filename.split('_')

    cmd = '_'.join(f_info[:-7])
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
        byte_sizes_dict[b_s.lower()] = 10**(i*3)

    #### Not sure why it was splitting by '_'
    #payload_num, payload_unit_num = \
    #    payload_size_str.split('_')
    
    payload_num, payload_unit_num = \
        payload_size_str.split(' ')

    return int(payload_num) * byte_sizes_dict[payload_unit_num]

def source_worker_to_value(s_w_str):
    s_w_arr = s_w_str.split('_')
    s = int(s_w_arr[1]) * 100
    w = int(s_w_arr[3])

    return s + w


def get_sorted_by_payload_mean_std_arrs(avg_cmd_dict, std_cmd_dict):

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


def get_sorted_source_worker_mean_std_arrs(
        source_worker_avg_dict,
        source_worker_std_dict):

    
    sorted_by_source_pair = sorted(source_worker_avg_dict.items(), 
        key=lambda kv: source_worker_to_value(kv[0]))

    #print(source_worker_avg_dict['s_1_w_1.csv'])
    #print(source_worker_std_dict['s_1_w_1.csv'])

    sorted_by_source_keys = [k for k,_ in sorted_by_source_pair]
    
    avg_dict = defaultdict(list)
    std_dict = defaultdict(list)

    first_cmd_dict = sorted_by_source_pair[0][1]

    for cmd, _ in first_cmd_dict.items():
        for source_worker_key in sorted_by_source_keys:
            avg_dict[cmd].append(source_worker_avg_dict[source_worker_key][cmd])
            std_dict[cmd].append(source_worker_std_dict[source_worker_key][cmd])

    return avg_dict, std_dict, sorted_by_source_keys

def get_sorted_clients(avg_clients_dict, std_clients_dict):

    sorted_avg_pair = sorted(avg_clients_dict.items(), 
        key=lambda kv: int(kv[0].split('_')[1]))
    sorted_std_pair = sorted(std_clients_dict.items(), 
        key=lambda kv: int(kv[0].split('_')[1]))

    sorted_size_keys = [k for k,_ in sorted_avg_pair]

    return sorted_avg_pair, sorted_std_pair, sorted_size_keys

def plot_cmds(title,
                avg_cmd_dict, std_cmd_dict,
                ticks_labels, filename, csv_dir):
    cmd_list = ["SET", "GET", "RPUSH", "LPUSH"]
    cmd_color_dict = {
        "SET": 'b',
        "GET": 'r',
        "RPUSH": 'g',
        "LPUSH": 'y'
    }

    font = {
        'size': 22,
    }
    label_size = 20
    label_pad_y = 15
    label_pad_x = 10

    width = 0.35

    plt.figure(figsize=(9,5))

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

    plt.ylabel('Throughput\n(requests/s)', fontdict=font, labelpad=label_pad_y)
    plt.xlabel('Data-sizes', fontdict=font, labelpad=label_pad_x)

    plt.tick_params(labelsize=label_size)
    plt.xticks(ind + (i-1)*width/2, ticks_labels)
    #plt.xticks(ind, ticks_labels)
    plt.tight_layout()
    plt.legend(loc='best', fontsize=label_size)

    #plt.title(title)
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

    font = {
        'size': 22,
    }
    label_size = 20
    label_pad_y = 15
    label_pad_x = 10

    '''
    dim_1 = 1
    dim_2 = 2
    fig, ax = plt.subplots(dim_1, dim_2, #sharex=True,
        figsize=(20,7))

    for i, cmd in enumerate(cmd_list):
        if i >= dim_1*dim_2:
            break
        for client_key, cmds_dict in avg_clients_cmds:
            avg_cmd_val_arr = cmds_dict[cmd]
            
            n_vars = len(avg_cmd_val_arr) + 1
            x_ticks = [payload_size_to_int(ds) for ds in ticks_labels]

            ax_curr = ax[i]
            ax_curr.plot(x_ticks, avg_cmd_val_arr, label=client_key, linestyle='--', marker='o')

            ax_curr.set_xscale('log')
            #ax_curr.set_xscale('linear')

            ax_curr.set_xticks(x_ticks)
            ax_curr.set_xticklabels(ticks_labels, rotation="vertical")

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
    '''
    ##########################################################
    #### Plotting SET cmd
    ##########################################################
    print(avg_clients_cmds)
    exit()
    plt.figure(figsize=(9,5))

    i = 0

    avg_val_arr = avg_cmd_dict['SET']
    std_val_arr = std_cmd_dict['SET']
    
    n_vars = len(avg_val_arr)

    assert n_vars == len(std_val_arr), "number of vars must be equal to data length"

    x_ticks = [payload_size_to_int(ds) for ds in ticks_labels]

    ind = np.arange(n_vars)
    plt.xscale('log')
    plt.plot(x_ticks, avg_val_arr, label=client_key, linestyle='--', marker='o')

    plt.ylabel('Throughput (requests/s)', fontdict=font, labelpad=label_pad_y)
    plt.xlabel('Data-sizes', fontdict=font, labelpad=label_pad_x)

    plt.tick_params(labelsize=label_size)
    plt.xticks(ticks_labels)
    #plt.xticks(ind, ticks_labels)
    plt.tight_layout()
    plt.legend(loc='best', fontsize=label_size)

    #plt.title(title)
    #plt.show()

    plots_dir = filename.split('/')[0]

    plots_full_path = os.path.join(csv_dir, plots_dir)
    if not os.path.exists(plots_full_path):
        os.makedirs(plots_full_path)

    print(os.path.join(csv_dir, filename))
    plt.savefig(os.path.join(csv_dir, filename))

    plt.clf()

    ##########################################################
    #### Plotting GET cmd
    ##########################################################

    


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

    avg_cmd_dict, std_cmd_dict, ticks_labels = \
        get_sorted_by_payload_mean_std_arrs(avg_cmd_dict, std_cmd_dict)

    plot_filename = "plots/cmds_rb_plot_c_%d_n_%d_d_%d.%s" % \
         (n_cli, n_reqs, len(ticks_labels), graph_ext)

    if do_plot:
        print("plotting - compare_cmds")
        title = "redis-benchmark (%s client & %s requests)" % \
            (n_cli, n_reqs)
        plot_cmds(title,
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

    n_clients = 0
    for entry in os.scandir(clients_dir):
        if entry.is_dir(follow_symlinks=False):
            if entry.name in ["temp", "plots", "plots_0"]:
                continue
            n_cli, n_reqs, avg_cmd_dict, std_cmd_dict, ticks_labels = \
                compare_cmds(entry, stop_at, do_plot=True)

            client_key = "c_" + str(n_cli)
            avg_clients_dict[client_key] = avg_cmd_dict
            std_clients_dict[client_key] = std_cmd_dict
            n_clients+=1

    avg_clients_cmds, std_clients_cmds, clients_labels = \
        get_sorted_clients(avg_clients_dict, std_clients_dict)

    plot_filename = "plots/clients_rb_plot_c_%d_n_%d_d_%d.%s" % \
         (n_cli, n_reqs, len(ticks_labels), graph_ext)

    plot_clients(n_cli, n_reqs,
        avg_clients_cmds,
        clients_labels, ticks_labels,
        plot_filename, clients_dir)


def compare_sources_and_workers(datasize_dir, stop_at, do_plot=True):
    avg_payload_dict = defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(float)
                        )
                    )
    std_payload_dict = defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(float)
                        )
                    )

    csv_num = 0
    for payload_size in os.scandir(datasize_dir):
        if payload_size.is_dir(follow_symlinks=False):
            csv_num = 0
            for csv_entry in scandir_csv(payload_size):
                pure_cmd_dict = csv_to_dict(csv_entry, stop_at)

                for cmd, req_rate_arr in pure_cmd_dict.items():
                    file_key = csv_entry.name.split('.')[0]
                    avg_payload_dict[payload_size.name][file_key][cmd] = np.mean(req_rate_arr)
                    std_payload_dict[payload_size.name][file_key][cmd] = np.std(req_rate_arr)

                csv_num += 1

    if do_plot:
        print("plotting - compare_sources_and_workers")
        for payload_size, _ in sorted(avg_payload_dict.items(), 
                    key=lambda kv: payload_size_to_int(kv[0])):
            source_worker_avg_dict = avg_payload_dict[payload_size]
            source_worker_std_dict = std_payload_dict[payload_size]

            avg_cmd_dict, std_cmd_dict, ticks_labels = \
                get_sorted_source_worker_mean_std_arrs(
                    source_worker_avg_dict,
                    source_worker_std_dict)

            plot_filename = "plots/source_worker_rb_plot_d_%s_csv_%d.%s" % \
                 (payload_size, csv_num, graph_ext)
            
            payload_num = payload_size.split('_')[0]
            payload_unit = payload_size.split('_')[1]
            title = "redis-benchmark Source/Worker %s %s" % \
                (payload_num, payload_unit.upper())
            plot_cmds(title,
                avg_cmd_dict, std_cmd_dict,
                ticks_labels, plot_filename, datasize_dir + "../")



def s_main(args):
    csv_dir = args['csv_dir']
    stop_at = int(args['stop_at'])
    analysis_type = int(args['analysis_type'])

    if analysis_type == 1:
        compare_cmds(csv_dir, stop_at)
    elif analysis_type == 2:
        compare_clients_num(csv_dir, stop_at)
    elif analysis_type == 3:
        compare_sources_and_workers(csv_dir, stop_at)


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
