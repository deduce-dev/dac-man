import os
import sys
import csv

import matplotlib.pyplot as plt

font = {
    'size': 22,
}
label_size = 20
label_pad_y = 15
label_pad_x = 10
#graph_ext = "png"
graph_ext = "pdf"

def find_marked_points(x_values, y_values, 
                vals_to_find_x, vals_to_find_y):
    markers_on = []

    j = 0
    for i, x_val in enumerate(x_values):
        val = vals_to_find_x[j]
        if abs(val - x_val) < 20:
            markers_on.append(i)
            j += 1
            if j < len(vals_to_find_x):
                continue
            else:
                break

    j = 0
    for i, y_val in enumerate(y_values):
        val = vals_to_find_y[j]
        if abs(val - y_val) < 20:
            markers_on.append(i)
            j += 1
            if j < len(vals_to_find_y):
                continue
            else:
                break

    return markers_on

def plot_from_csv(csv_files, output_dir_path):
    ###############################################
    x_values = []
    y_values = []

    with open(csv_files[0], 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            x_values.append(float(row[0]))
            y_values.append(int(row[1]))

    first_timestamp = min(x_values)
    x_values = [k-first_timestamp for k in x_values]

    markers_on = find_marked_points(x_values, y_values, 
        [1343.4419553279877], [0, 1500, 0])
    print(markers_on)

    plt.figure(figsize=(9,5))
    mark_every = 50

    #plt.plot(x_values, y_values, '--bD',  marker='^', markevery=markers_on, label="Workload 1")
    plt.plot(x_values, y_values, ':bD',  marker='o', markevery=mark_every, label="Workload 1")
    #plt.scatter(x_values, y_values, marker='^', label="Workload 1")

    ###############################################
    x_values = []
    y_values = []

    with open(csv_files[1], 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            x_values.append(float(row[0]))
            y_values.append(int(row[1]))

    first_timestamp = min(x_values)
    x_values = [k-first_timestamp for k in x_values]

    markers_on = find_marked_points(x_values, y_values, 
        [1350.5217807292938], [0, 2000, 0])
    print(markers_on)
    
    #plt.plot(x_values, y_values, '--gD',  marker='x', markevery=markers_on, label="Workload 2")
    plt.plot(x_values, y_values, ':gD',  marker='x', markevery=mark_every, label="Workload 2")
    #plt.scatter(x_values, y_values, marker='x', label="Workload 2")

    ###############################################
    x_values = []
    y_values = []

    with open(csv_files[2], 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            x_values.append(float(row[0]))
            y_values.append(int(row[1]))

    first_timestamp = min(x_values)
    x_values = [k-first_timestamp for k in x_values]

    markers_on = find_marked_points(x_values, y_values, 
        [1407.956473827362], [0, 2500, 0])
    print(markers_on)
    
    #plt.plot(x_values, y_values, '--rD', marker='+', markevery=markers_on, label="Workload 3")
    plt.plot(x_values, y_values, ':rD', marker='^', markevery=mark_every, label="Workload 3")
    #plt.plot(x_values, y_values, '--rD', , label="Workload 3")

    plt.tick_params(labelsize=label_size)
    plt.ylabel('Number of tasks\nin Task Queue', fontdict=font, labelpad=label_pad_y)
    plt.xlabel('time (s)', fontdict=font, labelpad=label_pad_x)
    plt.tight_layout()
    plt.legend(loc='best', fontsize=label_size)
    plt.ylim(top=3000)

    #plt.show()

    #name = "task_count_plot"
    name = "burst"
    output_full_path = os.path.join(output_dir_path, 
            '%s.%s' % (name, graph_ext))

    plt.savefig(output_full_path, bbox_inches='tight')


def s_main(args):
    #task_queue = "task_queue:f5b4873137a332836e384ecbc8c9a4a876d267f2"
    #csv_file = args['csv_file']
    output_dir = args['output_dir']

    csv_files = [
        "/Users/absho/workspace/lbnl/deduce/output_dir/aug_2019_experiments/setup_lean-worker0.16/data_size_100_percent/cori_N_1_n_64_3000/1500_2/job_count_sorted.csv",
        "/Users/absho/workspace/lbnl/deduce/output_dir/aug_2019_experiments/setup_lean-worker0.16/data_size_100_percent/cori_N_1_n_64_3000/2000_1/job_count_sorted.csv",
        "/Users/absho/workspace/lbnl/deduce/output_dir/aug_2019_experiments/setup_lean-worker0.16/data_size_100_percent/cori_N_1_n_64_3000/2500_1/job_count_sorted.csv"
    ]

    plot_from_csv(csv_files, output_dir)


if __name__ == "__main__":
    '''
    if (len(sys.argv) < 3):
            print("Usage: python read_job_count.py <csv_file> <output_dir>")
    else:
        args = {
            'csv_file': sys.argv[1],
            'output_dir': sys.argv[2]
        }
        s_main(args)
    '''

    if (len(sys.argv) < 2):
        print("Usage: python read_job_count.py <output_dir>")
    else:
        args = {
            'output_dir': sys.argv[1]
        }
        s_main(args)