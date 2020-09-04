import argparse
import numpy as np
from deduce_stream import StreamSrc

def main(host, port, dataset_iterator, stats_dir):
    stream_src = StreamSrc()
    stream_src.set_cache(host, port)
    stream_src.set_stats_dir(stats_dir)

    stream_src.set_dataset_iterator(dataset_iterator)
    stream_src.stream()


###################
# Data stream transformation
def transform_stream(dataset_len=100):
    for i in range(dataset_len):
        window_key_val = i
        yield [np.random.uniform(), np.random.uniform()]


###################
# For creating tasks with two datablocks
#
# python source.py -r redis-host -p redis-port -o stats_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="fluxnet streaming source",
                                     prog="source.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r', '--redis_host', type=str, required=True, help='Redis host')
    parser.add_argument('-p', '--redis_port', type=int, required=True, help='Redis port')
    parser.add_argument('-o', '--output_stats_dir', type=str, help='output stats directory')

    args = parser.parse_args()

    fn = transform_stream

    main(args.redis_host, args.redis_port, fn,
         args.output_stats_dir)
