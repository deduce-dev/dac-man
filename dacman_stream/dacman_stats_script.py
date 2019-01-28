import os
import csv
import numpy as np


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
    mydict = {}
    with open(csvfile, mode='r') as infile:
        reader = csv.reader(infile)
        mydict = {rows[0]:rows[1] for rows in reader}

    return mydict


###########################################################

output_dir_path = "/Users/absho/workspace/lbnl/deduce/output_dir/started_dir/"

output_full_path = os.path.join(output_dir_path, 'turnaround_start.csv')
turnaround_start = csv_to_dict(output_full_path)

output_full_path = os.path.join(output_dir_path, 'latency_start.csv')
latency_start = csv_to_dict(output_full_path)

finished_jobs_time = {}
output_dir_path = "/Users/absho/workspace/lbnl/deduce/output_dir/finished_dir/"

for entry in scandir_csv(output_dir_path):
    #### Checking if the file has the right extention
    if os.path.splitext(entry.name)[1] not in ['.csv']:
        continue
    finished_jobs_time.update(csv_to_dict(entry))

turnaround_values = []
latency_values = []
for key, _ in finished_jobs_time.items():
    turaround_value = float(finished_jobs_time[key]) - float(turnaround_start[key])
    turnaround_values.append(turaround_value)

    latency_value = float(finished_jobs_time[key]) - float(latency_start[key])
    latency_values.append(latency_value)

#print("turnaround_values: ", str(turnaround_values))
#print("latency_values: ", str(latency_values))

print("Average Turnaround: ", np.mean(turnaround_values))
print("Average Latency: ", np.mean(latency_values))
