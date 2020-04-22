import os

DATA_DIR = "/data"
if os.environ.get('STREAM_HPC_EVAL_DIR') is not None:
	DATA_DIR = os.environ.get('STREAM_HPC_EVAL_DIR')
	
PLOT_DIR = os.path.join(DATA_DIR, "plots")
EXPERIMENT_DIR = os.path.join(DATA_DIR, "streaming_eval_measurements")
SOURCE_DIR = "sources"
WORKER_DIR = "workers"
CSV_SOURCE_DICTS_DIRS = ["data_task_send_start", "data_task_send_end"]
CSV_WORKER_DICTS_DIRS = ["data_pull_start", "data_pull_end", "job_end_processing", "job_end_data_put"]
