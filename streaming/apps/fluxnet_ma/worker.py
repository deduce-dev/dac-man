import argparse
from deduce_stream.worker import StreamProcessingWorker

def main(host, port, analysis_operator, stats_dir):
    worker = StreamProcessingWorker(host, port)
    worker.set_stats_dir(stats_dir)

    worker.set_analysis_operator(analysis_operator)
    worker.process()


###################
# Data stream transformation
def calc_avg(dataA, dataB):
    return (float(dataA) + float(dataB))/2.0


###################
# Usage:
# python worker.py -r redis-host -p redis-port -o stats_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="fluxnet processing worker",
                                     prog="worker.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r', '--redis_host', type=str, required=True, help='Redis host')
    parser.add_argument('-p', '--redis_port', type=str, required=True, help='Redis port')
    parser.add_argument('-o', '--output_stats_dir', type=str, help='output stats directory')

    args = parser.parse_args()

    fn = calc_avg

    main(args.redis_host, args.redis_port, fn,
         args.output_stats_dir)
