import argparse
import numpy as np
from deduce_stream import StreamSrc

def main(host, port, dataset_iterator,
         stats_dir):
    stream_src = StreamSrc()
    stream_src.set_cache(host, port)
    stream_src.set_stats_dir(stats_dir)

    stream_src.set_dataset_iterator(dataset_iterator)
    stream_src.stream()


###################
# Data stream transformation
def transform_stream(n_frames=100, image_size=1000):
    matrix1 = np.random.rand(image_size)

    for i in range(1, n_frames):
        matrix2 = np.random.rand(image_size)

        yield [matrix1.tobytes(), matrix2.tobytes()]

        matrix1 = matrix2


###################
# Usage with Image data, for creating tasks with two datablocks
# python source.py -r redis-host -p redis-port -o stats_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Image Analysis streaming source",
                                     prog="source.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r', '--redis_host', type=str, required=True, help='Redis host')
    parser.add_argument('-p', '--redis_port', type=int, required=True, help='Redis port')
    parser.add_argument('-o', '--output_stats_dir', type=str, help='output stats directory')

    args = parser.parse_args()

    fn = transform_stream

    main(args.redis_host, args.redis_port, fn,
         args.output_stats_dir)
