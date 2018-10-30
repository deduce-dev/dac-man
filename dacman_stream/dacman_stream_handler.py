import os
import sys
import h5py
import redis
import copy
import uuid
import numpy as np
from datetime import datetime
from hashlib import blake2b
from math import sqrt
from scipy import stats
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

import settings as _settings

r = redis.Redis(
    host=_settings.HOST,
    port=_settings.PORT,
    db=_settings.DATABASE
)

startTime = datetime.now()

def create_main_hash_strings():
    hash_task_queue = blake2b(digest_size=20)
    hash_task_queue.update(_settings.TASK_QUEUE_NAME.encode('utf-8'))
    task_queue_hash_string = "%s:%s" % (_settings.TASK_QUEUE_NAME, hash_task_queue.hexdigest())

    hash_job_ordered_list = blake2b(digest_size=20)
    hash_job_ordered_list.update(_settings.JOB_ORDERED__LIST.encode('utf-8'))
    job_ordered_list_hash_string = "%s:%s" % (_settings.JOB_ORDERED__LIST, hash_job_ordered_list.hexdigest())

    return task_queue_hash_string, job_ordered_list_hash_string


def publish_tasks(task_queue_hs, job_o_list_hs, dataA, dataB):
    hash1 = blake2b(digest_size=20)
    hash2 = blake2b(digest_size=20)

    hash1.update(dataA)
    hash2.update(dataB)

    hash1_string = "%s:%s" % (_settings.DATABLOCK_PREFIX, hash1.hexdigest())
    hash2_string = "%s:%s" % (_settings.DATABLOCK_PREFIX, hash2.hexdigest())

    r.set(hash1_string, dataA.tostring())
    r.set(hash2_string, dataB.tostring())

    #### Adding the task to the ordered job list
    task_uuid = "%s:%s" % (_settings.TASK_PREFIX, str(uuid.uuid4()))
    r.rpush(job_o_list_hs, task_uuid)

    #print(task_queue_hash_string)
    r.lpush(task_queue_hs, (task_uuid, hash1_string, hash2_string, "custom"))


def two_frame_analysis(loopstep, source_dir, dataset, output_dir='.'):
    mean_correct = False
    use_gaussian_filter = False
    do_ttest = True
    add_to_fix_log=False

    task_queue_hash_string, job_ordered_list_hash_string = create_main_hash_strings()

    fx = h5py.File(os.path.join(source_dir, dataset), 'r')

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
                    publish_tasks(task_queue_hash_string, job_ordered_list_hash_string, matrix1, matrix2)
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
                

                #print(np.fromstring(r.get(hash1_string), dtype='<f4'))

                #print(datetime.now() - startTime)
                #exit()
        

def diff_edf_a(source_dir, dataset, output_dir):
    loopstep = 1 #1 = look at every frame; 2 = look at every other frame; 3 = look at every third frame; etc

    #============20160904_043848_CSPbI3_140DEG1_
    save_str = '/Users/absho/workspace/lbnl/deduce/src/juli_ALS/'
    start_str = '/Users/absho/workspace/lbnl/deduce/src/juli_ALS/'

    two_frame_analysis(loopstep, source_dir, dataset, output_dir)   

    
if __name__ == "__main__":

    if (len(sys.argv) < 4):
            print("Usage: python dacman_stream_handler.py <source_dir> <dataset(h5_file)> <output_dir>")
    else:
        source_dir = os.path.abspath(sys.argv[1])
        dataset = sys.argv[2]
        output_dir = os.path.abspath(sys.argv[3])

        diff_edf_a(source_dir, dataset, output_dir)
        print(datetime.now() - startTime)