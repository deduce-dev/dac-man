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

CSV_DICTS_DIRS = ["data_pull_start", "data_pull_end", "job_end_data_put"]

#OUTPUT_CSV_DIR = "/Users/absho/workspace/lbnl/deduce/output_dir/finished_dir/"
OUTPUT_CSV_DIR = "/global/homes/e/elbashan/workspace/dac-man/sandbox/job_finished_timestamp_dir/"

#srun -N 2 -n 8 -t 00:30:00 -o leanworker_out -e leanworker_err shifter -v --workdir=/project --image=aaelbashandy/dac-man:lean-worker0.5 python3 stream_worker.py blot.lbl.gov 6378 0 task_queue:f5b4873137a332836e384ecbc8c9a4a876d267f2
#scp elbashan@edison.nersc.gov:/global/homes/e/elbashan/workspace/dac-man/sandbox/job_finished_timestamp_dir/*.csv ./
