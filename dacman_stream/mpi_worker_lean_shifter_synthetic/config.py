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