import os
import sys
import h5py
import numpy as np
import time

data_pull_start = {}
data_pull_end = {}
job_end_processing = {}
job_end_data_put = {}


def write_to_csv():
    output_dir_path = _config.OUTPUT_CSV_DIR

    name = _config.CSV_DICTS_DIRS[0]
    output_full_path = os.path.join(output_dir_path, name, 
            '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in data_pull_start.items():
            writer.writerow([key, value])

    name = _config.CSV_DICTS_DIRS[1]
    output_full_path = os.path.join(output_dir_path, name, 
            '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in data_pull_end.items():
            writer.writerow([key, value])

    name = _config.CSV_DICTS_DIRS[2]
    output_full_path = os.path.join(output_dir_path, name, 
            '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in job_end_processing.items():
            writer.writerow([key, value])

    name = _config.CSV_DICTS_DIRS[3]
    output_full_path = os.path.join(output_dir_path, name, 
            '%s_%s_%s.csv' % (name, socket.gethostname(), os.getpid()))

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in job_end_data_put.items():
            writer.writerow([key, value])


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


def get_change_pairs(queue_hash, job_list_hash, loopstep, source_dir, dataset, output_dir='.', streaming_time=5):
    mean_correct = False
    use_gaussian_filter = False
    do_ttest = True
    add_to_fix_log=False

    fx = h5py.File(os.path.join(source_dir, dataset), 'r')

    for group in fx:
        print("group: " + str(group))
        for subgroup in fx[group]:
            print("subgroup: " + str(subgroup))
            frames_list = list(fx[group][subgroup])

            n_frames = len(frames_list)

            print("n_frames:", n_frames)

            t_end = time.time() + 60 * streaming_time
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

            while ii <= 3000:
                if ii == n_frames-1:
                    ii = 0
                jj = ii + 1

                filename2 = "/%s/%s/%s" % (group, subgroup, frames_list[jj])
                dx2 = fx[filename2] 
                
                log_mat_pos2 = dx2[:frame_len]
                matrix2 = log_mat_pos2.flatten()

                yield (matrix_temp, matrix2)
                
                matrix_temp = np.copy(matrix2)
                ii += 1

                #print(datetime.now() - startTime)
                #exit()


def collection_diff_mpi():
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
        change_pair_num = 0
        closed_workers = 0
        num_workers = size - 1
      
        for change_pair in get_change_pairs():
            result = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            source = statsu.Get_source()
            tag = status.Get_tag()
    
            if tag == States.READY:
                comm.send(change_pair, dest=source, tag=States.START)

        while closed_workers < num_workers:
            result = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            source = statsu.Get_source()
            tag = status.Get_tag()

            comm.send(None, dest=MPI.ANY_SOURCE, tag=States.EXIT)
            if tag == States.EXIT:
                closed_workers += 1
    else:
        while True:
            comm.send(None, dest=0, tag=States.READY)
            change_pair = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()

            if tag == States.START:
                data_a = change_pair[0]
                data_b = change_pair[1]
                two_frame_analysis(data_a, data_b)
            elif tag == States.EXIT:
                comm.send(None, dest=0, tag=States.EXIT)
                break
