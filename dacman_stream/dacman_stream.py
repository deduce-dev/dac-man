import os
import sys
import h5py
import redis
import uuid
import time
import _thread
from datetime import datetime
from hashlib import blake2b

import csv

#from diffstream import DiffStream

#### Remove later
#sys.path.insert(0, '../../../redis_scripts')
from dacman_task_handler import two_frame_analysis
import settings as _settings

r = redis.Redis(
    host=_settings.HOST,
    port=_settings.PORT,
    db=_settings.DATABASE
)

startTime = datetime.now()

turnaround_start = {}
latency_start = {}

def create_main_hash_strings():
    hash_task_queue = blake2b(digest_size=20)
    hash_task_queue.update(_settings.TASK_QUEUE_NAME.encode('utf-8'))
    task_queue_hash_string = "%s:%s" % (_settings.TASK_QUEUE_NAME, hash_task_queue.hexdigest())

    hash_job_ordered_list = blake2b(digest_size=20)
    hash_job_ordered_list.update(_settings.JOB_ORDERED_LIST.encode('utf-8'))
    job_ordered_list_hash_string = "%s:%s" % (_settings.JOB_ORDERED_LIST, hash_job_ordered_list.hexdigest())

    return task_queue_hash_string, job_ordered_list_hash_string


def publish_tasks(task_queue_hs, job_o_list_hs, dataA, dataB):
    hash1 = blake2b(digest_size=20)
    hash2 = blake2b(digest_size=20)

    hash1.update(dataA)
    hash2.update(dataB)

    hash1_string = "%s:%s" % (_settings.DATABLOCK_PREFIX, hash1.hexdigest())
    hash2_string = "%s:%s" % (_settings.DATABLOCK_PREFIX, hash2.hexdigest())

    task_uuid = "%s:%s" % (_settings.TASK_PREFIX, str(uuid.uuid4()))

    ##### Collecting Stats #####
    turnaround_start[task_uuid] = time.time()
    ############################

    r.set(hash1_string, dataA.tostring())
    r.set(hash2_string, dataB.tostring())

    #### Adding the task to the ordered job list
    r.rpush(job_o_list_hs, task_uuid)

    r.lpush(task_queue_hs, (task_uuid, hash1_string, hash2_string, "custom"))

    ##### Collecting Stats #####
    latency_start[task_uuid] = time.time()
    ############################

    print("Pushed", task_uuid, "To", task_queue_hs)


def two_frame_analysis_publisher(queue_hash, job_list_hash, loopstep, source_dir, dataset, output_dir='.'):
    mean_correct = False
    use_gaussian_filter = False
    do_ttest = True
    add_to_fix_log=False

    fx = h5py.File(os.path.join(source_dir, dataset), 'r')

    ## Remove Later 10/25/2018
    docker_loop_count = 1


    for group in fx:
        for subgroup in fx[group]:
            files_list = list(fx[group][subgroup])
            frames_list = list(filter(lambda x: x.endswith(".edf"), files_list))

            n_frames = len(frames_list)

            print("n_frames:", n_frames)

            for ii in range(0,n_frames-1,loopstep):
                jj = ii +1

                filename1 = "/%s/%s/%s" % (group, subgroup, frames_list[ii])
                filename2 = "/%s/%s/%s" % (group, subgroup, frames_list[jj])
                dx1 = fx[filename1]
                dx2 = fx[filename2]         
                imagedata1 = dx1[0,:,:]
                imagedata2 = dx2[0,:,:]

                data1 = imagedata1
                data2 = imagedata2

                log_mat_pos1=data1 #
                log_mat_pos2=data2 #
                
                matrix1 = log_mat_pos1.flatten()
                matrix2 = log_mat_pos2.flatten()

                #print(type(matrix1))

                try:
                    publish_tasks(queue_hash, job_list_hash, matrix1, matrix2)
                    print("Count: %s" % str(docker_loop_count))
                    docker_loop_count += 1
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise

                ## Remove Later 10/25/2018
                if docker_loop_count > 150:
                    return

                #print(datetime.now() - startTime)
                #exit()
        

def printProcLine(diffstream):
    for line in diffstream.printProcStdout():
        print(line)


def diff_edf_a(source_dir, dataset, output_dir):
    loopstep = 1 #1 = look at every frame; 2 = look at every other frame; 3 = look at every third frame; etc

    #### Create the hashes of both the task queue and the 
    #### job ordered list
    task_queue_hash_string, job_ordered_list_hash_string = create_main_hash_strings()

    ## Commented out "Remove later" 10/25/2018
    '''
    diffstream = DiffStream(_settings.HOST,
                            _settings.PORT,
                            _settings.DATABASE,
                            task_queue_hash_string,
                            two_frame_analysis,
                            1)
    #### Start the diff process (waiting for tasks) 
    diffstream.start()
    '''

    try:
        #_thread.start_new_thread(printProcLine, (diffstream, ))

        two_frame_analysis_publisher(task_queue_hash_string, 
                            job_ordered_list_hash_string, 
                    loopstep, source_dir, dataset, output_dir)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        #diffstream.stop()
        raise

    while r.llen(task_queue_hash_string) > 0:
        time.sleep(2)
        print("Number of Tasks in Queue:", r.llen(task_queue_hash_string))

    #### wait for all jobs to finish
    time.sleep(5)
    ## Commented out "Remove later" 10/25/2018
    #diffstream.stop()

    
if __name__ == "__main__":

    if (len(sys.argv) < 4):
            print("Usage: python dacman_stream_.py <source_dir> <dataset(h5_file)> <output_dir>")
    else:
        source_dir = os.path.abspath(sys.argv[1])
        dataset = sys.argv[2]
        output_dir = os.path.abspath(sys.argv[3])

        diff_edf_a(source_dir, dataset, output_dir)
        print(datetime.now() - startTime)

        output_dir_path = "/Users/absho/workspace/lbnl/deduce/output_dir/started_dir/"
        output_full_path = os.path.join(output_dir_path, 'turnaround_start.csv')

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in turnaround_start.items():
               writer.writerow([key, value])

        output_full_path = os.path.join(output_dir_path, 'latency_start.csv')

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in latency_start.items():
               writer.writerow([key, value])
