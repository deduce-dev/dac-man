import os
import sys
import csv
from collections import defaultdict 
import numpy as np
import matplotlib.pyplot as plt


class RedisStatGenerator(object):
    def __init__(self, stop_at=30):
        self.stop_at = stop_at

    def get_filename_info(self, filename):
        # example format: set_get_c_1_n_1_20_mb.csv

        f_info = filename.split('_')

        cmd = '_'.join(f_info[:-7])
        n_cli = int(f_info[-6])
        n_reqs = int(f_info[-4])
        payload_size = ' '.join([f_info[-2], f_info[-1].split('.')[0].upper()])

        return cmd, n_cli, n_reqs, payload_size

    def scandir_csv(self, path):
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

    def csv_to_dict(self, csvfile):
        '''
        Convert a csv file to dict
        '''
        mydict = defaultdict(list)
        with open(csvfile, mode='r') as infile:
            reader = csv.reader(infile)
            for i, row in enumerate(reader):
                if i >= self.stop_at:
                    break
                mydict[row[0]].append(float(row[1]))

        return mydict

    def payload_size_to_int(self, payload_size_str):
        byte_sizes = ['B', 'KB', 'MB', 'GB']

        byte_sizes_dict = {}
        for i, b_s in enumerate(byte_sizes):
            byte_sizes_dict[b_s] = 10**(i*3)
            byte_sizes_dict[b_s.lower()] = 10**(i*3)
        
        payload_num, payload_unit_num = \
            payload_size_str.split(' ')

        return int(payload_num) * byte_sizes_dict[payload_unit_num]

    def get_sorted_by_payload_mean_std_arrs(self, avg_cmd_dict, std_cmd_dict):
        first_cmd = list(avg_cmd_dict.keys())[0]

        sorted_size_pair = sorted(avg_cmd_dict[first_cmd].items(), 
            key=lambda kv: self.payload_size_to_int(kv[0]))

        sorted_size_keys = [k for k,_ in sorted_size_pair]
        
        avg_dict = defaultdict(list)
        std_dict = defaultdict(list)

        for cmd, _ in avg_cmd_dict.items():
            for size_key in sorted_size_keys:
                avg_dict[cmd].append(avg_cmd_dict[cmd][size_key])
                std_dict[cmd].append(std_cmd_dict[cmd][size_key])

        return avg_dict, std_dict, sorted_size_keys

    def get_sorted_clients(self, avg_clients_dict, std_clients_dict):
        sorted_avg_pair = sorted(avg_clients_dict.items(), 
            key=lambda kv: int(kv[0].split('_')[1]))
        sorted_std_pair = sorted(std_clients_dict.items(), 
            key=lambda kv: int(kv[0].split('_')[1]))

        sorted_size_keys = [k for k,_ in sorted_avg_pair]

        return sorted_avg_pair, sorted_std_pair, sorted_size_keys
    
    def compare_cmds(self, csv_dir):
        avg_cmd_dict = defaultdict(lambda: defaultdict(float))
        std_cmd_dict = defaultdict(lambda: defaultdict(float))

        n_cli = None
        n_reqs = None
        first_loop = True

        for entry in self.scandir_csv(csv_dir):
            _, n_cli_temp, n_reqs_temp, payload_size = self.get_filename_info(entry.name)

            if first_loop:
                n_cli = n_cli_temp
            elif n_cli != n_cli_temp:
                raise RuntimeError("Number of clients don't match")
            
            if first_loop:
                n_reqs = n_reqs_temp
            elif n_reqs != n_reqs_temp:
                raise RuntimeError("Number of requests don't match")
            
            first_loop = False

            pure_cmd_dict = self.csv_to_dict(entry)

            for cmd, req_rate_arr in pure_cmd_dict.items():
                avg_cmd_dict[cmd][payload_size] = np.mean(req_rate_arr)
                std_cmd_dict[cmd][payload_size] = np.std(req_rate_arr)

        avg_cmd_dict, std_cmd_dict, ticks_labels = \
            self.get_sorted_by_payload_mean_std_arrs(avg_cmd_dict, std_cmd_dict)

        return n_cli, n_reqs, avg_cmd_dict, std_cmd_dict, ticks_labels

    def compare_clients_num(self, clients_dir):

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
                    self.compare_cmds(entry)

                client_key = "c_" + str(n_cli)
                avg_clients_dict[client_key] = avg_cmd_dict
                std_clients_dict[client_key] = std_cmd_dict
                n_clients+=1

        avg_clients_cmds, std_clients_cmds, clients_labels = \
            self.get_sorted_clients(avg_clients_dict, std_clients_dict)

        return avg_clients_cmds, ticks_labels