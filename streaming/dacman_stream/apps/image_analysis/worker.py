import sys
import argparse
import numpy as np
from math import sqrt
from scipy import stats
from sklearn.metrics import mean_squared_error
from dacman_stream.worker import DacmanWorker

def main(host, port, analysis_operator, stats_dir):
    worker = DacmanWorker(host, port)
    worker.set_stats_dir(stats_dir)

    worker.set_analysis_operator(analysis_operator)
    worker.process()


###################
# Data stream transformation
def image_analysis(frameA, frameB):
    matrix1 = np.fromstring(frameA, dtype='<f4')
    matrix2 = np.fromstring(frameB, dtype='<f4')

    # compute RMSE between the 2 input frames
    rms = sqrt(mean_squared_error(matrix1, matrix2))
    # logarithm of RMSE
    rms_log = np.log(rms) 

    t_test_t, t_test_p = stats.ttest_ind(matrix1, matrix2, equal_var=True)
    
    return rms_log, t_test_t, t_test_p


###################
# Usage:
# python worker.py -r redis-host -p redis-port -o stats_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Image Analysis processing worker",
                                     prog="worker.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r', '--redis_host', type=str, required=True, help='Redis host')
    parser.add_argument('-p', '--redis_port', type=str, required=True, help='Redis port')
    parser.add_argument('-o', '--output_stats_dir', type=str, help='output stats directory')

    args = parser.parse_args()

    fn = image_analysis

    main(args.redis_host, args.redis_port, fn,
         args.output_stats_dir)
