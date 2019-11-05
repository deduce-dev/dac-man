import os
import sys
import h5py
import redis
import uuid
import time
import _thread
import numpy as np
from datetime import datetime
from hashlib import blake2b

import csv

import settings as _settings


start_time = time.time()

total_time = None
read_h5_time = None

data_send_start = {}
data_send_end = {}

def get_redis_instance(host, port, db=0):
    '''
    Return a redis instance with the given config
    '''
    try: 
        r = redis.Redis(
            host=host,
            port=port
        )
    except ValueError as e:
        raise e("Couldn't connect to Redis")
    
    return r

def create_main_hash_strings():
    hash_task_queue = blake2b(digest_size=20)
    hash_task_queue.update(_settings.TASK_QUEUE_NAME.encode('utf-8'))
    task_queue_hash_string = "%s:%s" % (_settings.TASK_QUEUE_NAME, hash_task_queue.hexdigest())

    hash_job_ordered_list = blake2b(digest_size=20)
    hash_job_ordered_list.update(_settings.JOB_ORDERED_LIST.encode('utf-8'))
    job_ordered_list_hash_string = "%s:%s" % (_settings.JOB_ORDERED_LIST, hash_job_ordered_list.hexdigest())

    return task_queue_hash_string, job_ordered_list_hash_string


def publish_tasks(r, task_queue_hs, job_o_list_hs, dataA, dataB):
    hash1 = blake2b(digest_size=20)
    hash2 = blake2b(digest_size=20)

    hash1.update(dataA)
    hash2.update(dataB)

    hash1_string = "%s:%s" % (_settings.DATABLOCK_PREFIX, hash1.hexdigest())
    hash2_string = "%s:%s" % (_settings.DATABLOCK_PREFIX, hash2.hexdigest())

    task_uuid = "%s:%s" % (_settings.TASK_PREFIX, str(uuid.uuid4()))

    ##### Collecting Stats #####
    data_send_start[task_uuid] = time.time()
    ############################

    r.set(hash1_string, dataA.tostring())
    r.set(hash2_string, dataB.tostring())

    #### Adding the task to the ordered job list
    r.rpush(job_o_list_hs, task_uuid)

    r.lpush(task_queue_hs, (task_uuid, hash1_string, hash2_string, "custom"))

    ##### Collecting Stats #####
    data_send_end[task_uuid] = time.time()
    ############################

    print("Pushed", task_uuid, "To", task_queue_hs)


def two_frame_analysis_publisher(
        r, queue_hash, job_list_hash,
        loopstep, dataset,
        streaming_time=5,
        data_fraction=1):
    mean_correct = False
    use_gaussian_filter = False
    do_ttest = True
    add_to_fix_log=False

    read_h5_start = time.time()
    fx = h5py.File(dataset, 'r')
    read_h5_end = time.time()

    read_h5_time = read_h5_end - read_h5_start

    ## Remove Later 10/25/2018
    docker_loop_count = 1

    for group in fx:
        print("group: " + str(group))
        for subgroup in fx[group]:
            print("subgroup: " + str(subgroup))
            files_list = list(fx[group][subgroup])
            frames_list = files_list

            n_frames = len(frames_list)

            print("n_frames:", n_frames)

            t_end = time.time() + 60 * streaming_time
            ii = 0

            filename1 = "/%s/%s/%s" % (group, subgroup, frames_list[ii])
            dx1 = fx[filename1]
            frame_len = len(dx1)
            frame_len = int(frame_len * data_fraction)
            log_mat_pos1 = dx1[:frame_len]
            matrix_temp = log_mat_pos1.flatten()

            while time.time() < t_end:
                if ii == n_frames-1:
                    ii = 0
                jj = ii + 1

                filename2 = "/%s/%s/%s" % (group, subgroup, frames_list[jj])
                dx2 = fx[filename2] 
                
                log_mat_pos2 = dx2[:frame_len]
                matrix2 = log_mat_pos2.flatten()

                try:
                    #time.sleep(0.5)
                    publish_tasks(r, queue_hash, job_list_hash, matrix_temp, matrix2)
                    print("Count: %s" % str(docker_loop_count))
                    docker_loop_count += 1
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
                
                matrix_temp = np.copy(matrix2)
                ii += 1

def printProcLine(diffstream):
    for line in diffstream.printProcStdout():
        print(line)


def diff_edf_a(r, dataset, streaming_time, data_fraction):
    loopstep = 1 #1 = look at every frame; 2 = look at every other frame; 3 = look at every third frame; etc

    #### Create the hashes of both the task queue and the 
    #### job ordered list
    task_queue_hash_string, job_ordered_list_hash_string = create_main_hash_strings()


    try:
        two_frame_analysis_publisher(r, task_queue_hash_string, 
                            job_ordered_list_hash_string, 
                            loopstep, dataset, streaming_time,
                            data_fraction)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    while r.llen(task_queue_hash_string) > 0:
        time.sleep(2)
        print("Number of Tasks in Queue:", r.llen(task_queue_hash_string))

    #### wait for all jobs to finish
    time.sleep(5)


def write_results(output_dir):
    #### Starting Saving Results
    output_full_path = os.path.join(output_dir, 'script_total_time.txt')
    with open(output_full_path, 'w') as txt_file:
        txt_file.write(total_time)

    output_full_path = os.path.join(output_dir, 'read_h5_time.txt')
    with open(output_full_path, 'w') as txt_file:
        txt_file.write(read_h5_start)
    
    output_full_path = os.path.join(output_dir, 'data_send_start.csv')
    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in data_send_start.items():
           writer.writerow([key, value])

    output_full_path = os.path.join(output_dir, 'data_send_end.csv')
    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in data_send_end.items():
           writer.writerow([key, value])


if __name__ == "__main__":

    if (len(sys.argv) != 7):
            print("Usage: python dacman_stream.py <redis_host> <redis_port> <dataset(h5_file)> <streaming_time> <data_fraction> <output_dir>")
    else:
        r_host = sys.argv[1]
        r_port = sys.argv[2]
        dataset = sys.argv[3]
        streaming_time = float(sys.argv[4])
        data_fraction = float(sys.argv[5])
        output_dir = os.path.abspath(sys.argv[6])

        r = get_redis_instance(r_host, r_port)

        diff_edf_a(r, dataset, streaming_time, data_fraction)
        end_time = time.time()
        total_time = end_time - start_time

        write_results(output_dir)
        
