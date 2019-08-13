import os
import sys
import csv
import h5py
import socket
import marshal, types
import numpy as np
import time
import uuid
from math import sqrt
from sklearn.metrics import mean_squared_error
from scipy import stats

from mpi4py import MPI

data_ready = {}
data_send_start = {}
data_send_end = {}
worker_ready = {}
data_pull_start = {}
data_pull_end = {}
job_end_processing = {}
job_end_data_put = {}

TASK_PREFIX = "task"
CSV_DICTS_DIRS = [
    "data_ready",
    "data_send_start",
    "data_send_end",
    "worker_ready",
    "data_pull_start",
    "data_pull_end",
    "job_end_processing",
    "job_end_data_put"
]

#os.environ["OPENBLAS_NUM_THREADS"] = "1"

OUTPUT_CSV_DIR = "/global/homes/e/elbashan/workspace/dac-man/sandbox/batch_timestamps_dir/"

def write_to_csv(rank=0):
    output_dir_path = OUTPUT_CSV_DIR

    if rank == 0:
        name = CSV_DICTS_DIRS[0]
        output_full_path = os.path.join(output_dir_path, name,
                '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in data_ready.items():
                writer.writerow([key, value])

        name = CSV_DICTS_DIRS[1]
        output_full_path = os.path.join(output_dir_path, name,
                '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in data_send_start.items():
                writer.writerow([key, value])

        name = CSV_DICTS_DIRS[2]
        output_full_path = os.path.join(output_dir_path, name,
                '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in data_send_end.items():
                writer.writerow([key, value])
    else:
        name = CSV_DICTS_DIRS[3]
        output_full_path = os.path.join(output_dir_path, name,
                '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in worker_ready.items():
                writer.writerow([key, value])

        name = CSV_DICTS_DIRS[4]
        output_full_path = os.path.join(output_dir_path, name,
                '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in data_pull_start.items():
                writer.writerow([key, value])

        name = CSV_DICTS_DIRS[5]
        output_full_path = os.path.join(output_dir_path, name,
                '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in data_pull_end.items():
                writer.writerow([key, value])

        name = CSV_DICTS_DIRS[6]
        output_full_path = os.path.join(output_dir_path, name,
                '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in job_end_processing.items():
                writer.writerow([key, value])

        name = CSV_DICTS_DIRS[7]
        output_full_path = os.path.join(output_dir_path, name,
                '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

        with open(output_full_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in job_end_data_put.items():
                writer.writerow([key, value])


def func_deserializer_file(file):
    '''
    Deserialize analyzer function from a file
    '''
    with open(file, 'rb') as f:
        code = marshal.load(f)
    func = types.FunctionType(code, globals(), "analyzer")

    return func

#### Not using it anymore to match the dacman_stream behavior
#### by loading the serialized function instead using
#### func_deserializer_file(file)
def two_frame_analysis(data_a, data_b):
    rms_log = None
    t_test_t = None
    t_test_p = None
    do_ttest = True

    matrix1 = data_a
    matrix2 = data_b

    #matrix1 = dataA.flatten()
    #matrix2 = dataB.flatten()

    rms = sqrt(mean_squared_error(matrix1, matrix2)) #compute RMSE between the 2 input frames
    min_d = min(min(matrix1), min(matrix2))
    max_d = max(max(matrix1), max(matrix2))
    
    rms_log = np.log(rms) #logarithm of RMSE

    if do_ttest:
        #option 1: t-test over the whole frame
        t_test_t, t_test_p = stats.ttest_ind(matrix1, matrix2, equal_var=True)
    
    return rms_log, t_test_t, t_test_p


def get_change_pairs(dataset, job_num=3000):
    mean_correct = False
    use_gaussian_filter = False
    do_ttest = True
    add_to_fix_log=False

    fx = h5py.File(dataset, 'r')

    for group in fx:
        print("group: " + str(group))
        for subgroup in fx[group]:
            print("subgroup: " + str(subgroup))
            frames_list = list(fx[group][subgroup])

            n_frames = len(frames_list)

            print("n_frames:", n_frames)

            ii = 0

            filename1 = "/%s/%s/%s" % (group, subgroup, frames_list[ii])
            dx1 = fx[filename1]
            #log_mat_pos1 = dx1[0,:,:]
            frame_len = len(dx1)
            frame_len = int(frame_len * 1)
            log_mat_pos1 = dx1[:frame_len]
            matrix_temp = log_mat_pos1.flatten()
            #matrix_temp = dx1
            #print(type(dx1))
            #print(frame_len)
            #exit()

            job_count = 0
            while job_count < job_num:
                if ii == n_frames-1:
                    ii = 0
                jj = ii + 1

                filename2 = "/%s/%s/%s" % (group, subgroup, frames_list[jj])
                dx2 = fx[filename2] 
                
                log_mat_pos2 = dx2[:frame_len]
                matrix2 = log_mat_pos2.flatten()

                task_uuid = "%s:%s" % (TASK_PREFIX, str(uuid.uuid4()))
                yield (task_uuid, matrix_temp, matrix2)
                
                matrix_temp = np.copy(matrix2)
                ii += 1
                job_count += 1

                #print(datetime.now() - startTime)
                #exit()
            print("Rank 0 finished sending jobs. # of jobs: %s" % \
                (str(job_count)))


def diff_edf_mpi(dataset, job_num):
    print("diff_edf_mpi() started")
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    status = MPI.Status()

    class States():
        READY = 0
        START = 1
        DONE = 2
        EXIT = 3

    if rank == 0:
        script_start_ts = time.time()
        print("Rank:", str(rank), "started")
        change_pair_num = 0
        closed_workers = 0
        num_workers = size - 1
        
        finished_jobs_count = 0

        for change_pair in get_change_pairs(dataset, job_num):
            pair_ready = time.time()
            while True:
                result = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
                source = status.Get_source()
                tag = status.Get_tag()
    
                if tag == States.READY:
                    task_uuid = change_pair[0]
                    data_ready[task_uuid] = pair_ready
                    data_send_start[task_uuid] = time.time()
                    comm.send(change_pair, dest=source, tag=States.START)
                    data_send_end[task_uuid] = time.time()
                    print("Rank:", str(rank), "pushed", task_uuid, "to Worker:", str(source))
                    break
                elif tag == States.DONE:
                    finished_jobs_count += 1
                else:
                    print("Rank 0: weird tag %s" % (str(tag)))

        while closed_workers < num_workers:
            result = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            source = status.Get_source()
            tag = status.Get_tag()

            if tag == States.EXIT:
                closed_workers += 1
            else:
                if tag == States.DONE:
                    finished_jobs_count += 1
                comm.send(None, dest=source, tag=States.EXIT)

        script_end_ts = time.time()
        #### Creating the output file that will have the stream output
        with open(os.path.join(OUTPUT_CSV_DIR, "dacman_batch_ts", 
            "dacman_batch_start_ts.txt"), 'w') as f:
            print(str(script_start_ts), file=f)
        with open(os.path.join(OUTPUT_CSV_DIR, "dacman_batch_ts", 
            "dacman_batch_end_ts.txt"), 'w') as f:
            print(str(script_end_ts), file=f)

        print("Rank 0: %s jobs has been processed" % (str(finished_jobs_count)))
    else:
        custom_analyzer = func_deserializer_file("func_analyzer_mpi.marshal")
        while True:
            w_ready = time.time()
            comm.send(None, dest=0, tag=States.READY)
            pull_start = time.time()
            change_pair = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            pull_end = time.time()
            tag = status.Get_tag()

            if tag == States.START:
                task_uuid = change_pair[0]
                data_a = change_pair[1]
                data_b = change_pair[2]
                #data_a = np.fromstring(change_pair[1], dtype='<f4')
                #data_b = np.fromstring(change_pair[2], dtype='<f4')

                worker_ready[task_uuid] = w_ready
                data_pull_start[task_uuid] = pull_start
                data_pull_end[task_uuid] = pull_end
                
                #two_frame_analysis(data_a, data_b)
                _, _, _ = custom_analyzer(data_a, data_b)
                job_end_processing[task_uuid] = time.time()
                comm.send(None, dest=0, tag=States.DONE)
                job_end_data_put[task_uuid] = time.time()

                print("Rank:", str(rank), "processed", task_uuid)
            elif tag == States.EXIT:
                comm.send(None, dest=0, tag=States.EXIT)
                break

    # Saving timestamps in CSV format
    write_to_csv(rank=rank)
    #print("Rank %s finished!" % (str(rank)))

if __name__ == "__main__":

    if (len(sys.argv) < 3):
            print("Usage: python dacman_batch.py <dataset(h5_file)> <job_num>")
    else:
        dataset = os.path.abspath(sys.argv[1])
        #output_dir = os.path.abspath(sys.argv[2])
        job_num = int(sys.argv[2])

        diff_edf_mpi(dataset, job_num)

