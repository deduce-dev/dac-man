import argparse
import numpy as np
from deduce_stream import WindowedStreamSrc

def main(host, port, dataset_iterator,
         window_size, key_name, stats_dir):
    stream_src = WindowedStreamSrc()
    stream_src.set_cache(host, port)
    stream_src.set_window_size(window_size)
    stream_src.set_window_key(key_name)
    stream_src.set_stats_dir(stats_dir)

    stream_src.set_dataset_iterator(dataset_iterator)
    stream_src.stream()


###################
# Data stream transformation
def transform_stream(dataset_len=100):
    for i in range(dataset_len):
        window_key_val = i
        yield window_key_val, [np.random.uniform()]


###################
# For creating tasks with two datablocks
#
# python source.py -s 2 -r redis-host -p redis-port -o stats_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Change-Detection streaming source",
                                     prog="source.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r', '--redis_host', type=str, required=True, help='Redis host')
    parser.add_argument('-p', '--redis_port', type=int, required=True, help='Redis port')
    parser.add_argument('-k', '--keyname', type=str, help='key name', default='datetime')
    parser.add_argument('-s', '--windowsize', type=int, help='window size', default=2)
    parser.add_argument('-o', '--output_stats_dir', type=str, help='output stats directory')

    args = parser.parse_args()

    fn = transform_stream

    main(args.redis_host, args.redis_port, fn,
        args.windowsize, args.keyname, args.output_stats_dir)
