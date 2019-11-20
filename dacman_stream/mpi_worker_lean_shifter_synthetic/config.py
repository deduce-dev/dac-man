HOST="redis"
PORT="6379"
#PORT="6378"
DATABASE=0

DEFAULT_EXECUTOR = 0
MPI_EXECUTOR = 1
EXECUTOR=MPI_EXECUTOR

DATABLOCK_PREFIX="datablock"
TASK_PREFIX="task"

TASK_QUEUE_NAME="task_queue"
JOB_ORDERED_LIST="job_ordered_list"

REDIS_QUEUE_ID="f5b4873137a332836e384ecbc8c9a4a876d267f2"
CUSTOM_ANALYZER_FILE="func_analyzer_mpi.marshal"

CSV_DICTS_DIRS = ["data_pull_start", "data_pull_end", "job_end_processing", "job_end_data_put"]

#OUTPUT_CSV_DIR = "/Users/absho/workspace/lbnl/deduce/output_dir/finished_dir/"
OUTPUT_CSV_DIR = "/global/homes/e/elbashan/workspace/dac-man/sandbox/job_finished_timestamp_dir/"

#srun -N 2 -n 20 -C haswell -t 00:45:00 -o leanworker_out -e leanworker_err shifter -v --workdir=/project --image=aaelbashandy/dac-man:lean-worker0.6 python3 stream_worker.py blot.lbl.gov 6378 0 task_queue:f5b4873137a332836e384ecbc8c9a4a876d267f2

####################################################################
#scp -r elbashan@edison.nersc.gov:/global/homes/e/elbashan/workspace/dac-man/sandbox/job_finished_timestamp_dir/* /Users/absho/workspace/lbnl/deduce/output_dir/finished_dir/
#scp -r elbashan@edison.nersc.gov:/global/homes/e/elbashan/workspace/dac-man/sandbox/job_finished_timestamp_dir/* output_1s_0/
#scp -r aaelbashandy@blot.lbl.gov:/home/portnoy/u0/aaelbashandy/workspace/dacman_dataset/dacman_source_output/* output_1s_0/

####################################################################
#python dacman_stream.py ../../dacman/deduce/juli_ALS/ 20160904_043848_CSPbI3_140DEG1_.h5 .
#python dacman_stream.py /dataset 20160904_043848_CSPbI3_140DEG1_.h5 . 5

####################################################################
#python dacman_stats_script.py /Users/absho/workspace/lbnl/deduce/output_dir/started_dir/N_10_n_100_datasize_100_wo_bursts/ /Users/absho/workspace/lbnl/deduce/output_dir/finished_dir/N_10_n_100_datasize_100_wo_bursts/ /Users/absho/workspace/lbnl/deduce/output_dir/stats_dir/experiment_2/ True
#python dacman_stats_script.py /Users/absho/workspace/lbnl/deduce/output_dir/started_dir/N_10_n_100_datasize_100_wo_bursts/output_0.4s_7/ /Users/absho/workspace/lbnl/deduce/output_dir/finished_dir/N_10_n_100_datasize_100_wo_bursts/output_0.4s_7/ /Users/absho/workspace/lbnl/deduce/output_dir/stats_dir/experiment_2/N_10_n_100_datasize_100_wo_bursts/ 0
#python dacman_stats_script.py /Users/absho/workspace/lbnl/deduce/output_dir/started_dir/N_10_n_200_datasize_100_wo_bursts_5min/ /Users/absho/workspace/lbnl/deduce/output_dir/finished_dir/N_10_n_200_datasize_100_wo_bursts_5min/ /Users/absho/workspace/lbnl/deduce/output_dir/stats_dir/experiment_2/N_10_n_200_datasize_100_wo_bursts_5min/ 1
#python dacman_stats_script.py /Users/absho/workspace/lbnl/deduce/output_dir/debugging/started_dir/ /Users/absho/workspace/lbnl/deduce/output_dir/debugging/finished_dir/ /Users/absho/workspace/lbnl/deduce/output_dir/debugging/output_dir/ 1



'''
dacman_data_source | Unexpected error: <class 'OSError'>
dacman_data_source | Traceback (most recent call last):
dacman_data_source |   File "dacman_stream.py", line 212, in <module>
dacman_data_source |     diff_edf_a(r, dataset, streaming_time, data_fraction)
dacman_data_source |   File "dacman_stream.py", line 162, in diff_edf_a
dacman_data_source |     data_fraction)
dacman_data_source |   File "dacman_stream.py", line 93, in two_frame_analysis_publisher
dacman_data_source |     fx = h5py.File(dataset, 'r')
dacman_data_source |   File "/home/dacman/.local/lib/python3.6/site-packages/h5py/_hl/files.py", line 408, in __init__
dacman_data_source |     swmr=swmr)
dacman_data_source |   File "/home/dacman/.local/lib/python3.6/site-packages/h5py/_hl/files.py", line 173, in make_fid
dacman_data_source |     fid = h5f.open(name, flags, fapl=fapl)
dacman_data_source |   File "h5py/_objects.pyx", line 54, in h5py._objects.with_phil.wrapper
dacman_data_source |   File "h5py/_objects.pyx", line 55, in h5py._objects.with_phil.wrapper
dacman_data_source |   File "h5py/h5f.pyx", line 88, in h5py.h5f.open
dacman_data_source | OSError: Unable to open file (unable to open file: name = '/data/hdf5_dataset/dataset_juli_synthetic_5.0m_0s.h5', errno = 2, error message = 'No such file or directory', flags = 0, o_flags = 0)

dacman_data_source | Unexpected error: <class 'OSError'>
dacman_data_source | Traceback (most recent call last):
dacman_data_source |   File "dacman_stream.py", line 212, in <module>
dacman_data_source |     diff_edf_a(r, dataset, streaming_time, data_fraction)
dacman_data_source |   File "dacman_stream.py", line 162, in diff_edf_a
dacman_data_source |     data_fraction)
dacman_data_source |   File "dacman_stream.py", line 93, in two_frame_analysis_publisher
dacman_data_source |     fx = h5py.File(dataset, 'r')
dacman_data_source |   File "/home/dacman/.local/lib/python3.6/site-packages/h5py/_hl/files.py", line 408, in __init__
dacman_data_source |     swmr=swmr)
dacman_data_source |   File "/home/dacman/.local/lib/python3.6/site-packages/h5py/_hl/files.py", line 173, in make_fid
dacman_data_source |     fid = h5f.open(name, flags, fapl=fapl)
dacman_data_source |   File "h5py/_objects.pyx", line 54, in h5py._objects.with_phil.wrapper
dacman_data_source |   File "h5py/_objects.pyx", line 55, in h5py._objects.with_phil.wrapper
dacman_data_source |   File "h5py/h5f.pyx", line 88, in h5py.h5f.open
dacman_data_source | OSError: Unable to open file (unable to open file: name = '/data/hdf5_dataset/dataset_juli_synthetic_5.0m_0s.h5', errno = 13, error message = 'Permission denied', flags = 0, o_flags = 0)


dacman_worker | Host:53ef5eac8d07-PID:1-MPIWorker:0 is processing task: b"('task:974d465c-1b64-4b74-aa84-c0faa4b98a87', 'datablock:7f41c7902d1c073d23586a348e98f6dd89c88f01', 'datablock:d00870be1da4459821035e5d78a6e7b56d793ce1', 'custom')"
dacman_worker | 
dacman_worker | Queue is empty
dacman_worker | Queue is empty
dacman_worker | Queue is empty
dacman_worker | Queue is empty
dacman_worker | Queue is empty
dacman_worker | Unexpected error: <class 'TypeError'>
dacman_worker | Traceback (most recent call last):
dacman_worker |   File "stream_worker.py", line 266, in <module>
dacman_worker |     s_main(args)
dacman_worker |   File "stream_worker.py", line 244, in s_main
dacman_worker |     diff_tasks(r, redis_queue_id, custom_analyzer, output_dir, is_mpi)
dacman_worker |   File "stream_worker.py", line 209, in diff_tasks
dacman_worker |     _thread.start_new_thread(write_to_csv, (output_dir))
dacman_worker | TypeError: 2nd arg must be a tuple

Host:d7db4c46fa1f-PID:1 Writing to csv to /data/results/workers/
dacman_worker | 
dacman_worker | failed_count: 3
dacman_worker | write_to_csv
dacman_worker | Unhandled exception in thread started by <function write_to_csv at 0x7f6307e3bc80>
dacman_worker | Traceback (most recent call last):
dacman_worker |   File "stream_worker.py", line 115, in write_to_csv
dacman_worker | AttributeError: 'NoneType' object has no attribute 'exists'


'''