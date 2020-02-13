import os
import sys
import time
import redis
import csv

import matplotlib.pyplot as plt

import settings as _settings

r = None

font = {
    'size': 22,
}
label_size = 20
label_pad_y = 15
label_pad_x = 10
graph_ext = "pdf"

def write_to_csv(timestamps_sorted, output_dir_path):

    name = "job_count_sorted"
    output_full_path = os.path.join(output_dir_path, 
            '%s.csv' % (name))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in timestamps_sorted:
            writer.writerow([key, value])

def plot_job_count(timestamps_sorted, output_dir_path):
    x_values = [k for k, _ in timestamps_sorted]
    y_values = [v for _, v in timestamps_sorted]
    
    first_timestamp = min(x_values)

    x_values = [k-first_timestamp for k in x_values]

    plt.plot(x_values, y_values)

    #plt.show()

    name = "job_count_plot"
    output_full_path = os.path.join(output_dir_path, 
            '%s.%s' % (name, graph_ext))

    plt.savefig(output_full_path)


def s_main(args):
    #task_queue = "task_queue:f5b4873137a332836e384ecbc8c9a4a876d267f2"
    task_queue = args['task_queue']
    task_list = args['task_list']

    r = redis.Redis(
        host=args['redis_server'],
        port=args['redis_port'],
        db=_settings.DATABASE
    )

    job_count_dict = {}

    failed_count = 0
    # job = task in our use case
    job_count = r.llen(task_queue)
    total_job_count = r.llen(task_list)

    while total_job_count < 3000:
        print("job_count", job_count)
        job_count_dict[time.time()] = job_count
        # 1 second resolution
        time.sleep(1)
        job_count = r.llen(task_queue)
        total_job_count = r.llen(task_list)

    d1 = job_count_dict
    timestamps_sorted = [(k, d1[k]) for k in sorted(d1.keys())]

    if timestamps_sorted:
        write_to_csv(timestamps_sorted, args['output_dir'])
        plot_job_count(timestamps_sorted, args['output_dir'])
    else:
        print("Redis queue is empty")


if __name__ == "__main__":
    if (len(sys.argv) < 6):
            print("Usage: python count_jobs_in_queue.py <redis_server> <redis_port> <task_queue> <task_list> <output_dir>")
    else:
        args = {
            'redis_server': sys.argv[1],
            'redis_port': sys.argv[2],
            'task_queue': sys.argv[3],
            'task_list': sys.argv[4],
            'output_dir': sys.argv[5]
        }
        s_main(args)