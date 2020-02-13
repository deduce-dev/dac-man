'''
Script to create the file structure for redis-benchmark results.

n_1000: # Number of requests
    c_64: # Number of clients
        set_get_c_64_n_1000_1_b.csv
        set_get_c_64_n_1000_50_b.csv
        set_get_c_64_n_1000_100_b.csv
        set_get_c_64_n_1000_500_b.csv
        set_get_c_64_n_1000_1_kb.csv
        set_get_c_64_n_1000_50_kb.csv
        set_get_c_64_n_1000_100_kb.csv
        set_get_c_64_n_1000_500_kb.csv
        set_get_c_64_n_1000_1_mb.csv
        set_get_c_64_n_1000_10_mb.csv
        set_get_c_64_n_1000_20_mb.csv
        plots/ # Dir for induced analysis plots
        temp/ # Dir for files that won't be processed.
    c_128:
        ...

Author: Abdelrahman Elbashandy - aaelbashandy@lbl.gov
'''
import sys
import os
import argparse

def main(args):
    print(args)

    cmds_str = '_'.join(args.commands)
    print(cmds_str)

    try:
        for n_requests in args.requests:
            for n_clients in args.clients:
                for data_size in args.data_sizes:
                    csv_file = "%s_c_%d_n_%d_d_%s.csv" % \
                        (cmds_str, n_clients, n_requests, data_size)
                    path = os.path.join(args.output_dir, "n_%d" % (n_requests))
                    path = os.path.join(path, "c_%d" % (n_clients))
                    
                    if not os.path.exists(path):
                        try:
                            os.makedirs(path)
                        except OSError as exc: # Guard against race condition
                            if exc.errno != errno.EEXIST:
                                raise

                    path = os.path.join(path, csv_file)
                    with open(path, "w") as my_empty_csv:
                        # now you have an empty file already
                        pass  # or write something to it already
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s" % path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Create the file structure for redis-benchmark results"
    )
    parser.add_argument("-c", dest="clients",
        help="Number of clients", type=int, nargs="+")
    parser.add_argument("-n", dest="requests",
        help="Number of requests", type=int, nargs="+")
    parser.add_argument("-d", dest="data_sizes",
        help="Data Sizes that will be tested on", nargs="+")
    parser.add_argument("-t", dest="commands",
        help="Redis commands that will be test on", nargs="+")
    parser.add_argument("-o", "--output-dir",
        help="Create the structure at this directory")
    args = parser.parse_args()

    main(args)
