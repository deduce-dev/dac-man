import sys
import os
import argparse
import h5py
from dacman_stream.source import BasicStreamSrc

def main(host, port, dataset_iterator, dataset_src,
         stats_dir):
    stream_src = BasicStreamSrc(host, port)
    stream_src.set_stats_dir(stats_dir)

    stream_src.set_dataset_iterator(dataset_iterator)
    stream_src.stream(dataset_src)


###################
# Data stream transformation
def transform_als_stream(dataset, data_fraction=1):
    fx = h5py.File(dataset, 'r')

    for group in fx:
        for subgroup in fx[group]:
            frames_list = list(fx[group][subgroup])

            n_frames = len(frames_list)

            filename1 = "/%s/%s/%s" % (group, subgroup, frames_list[0])
            dx1 = fx[filename1]
            frame_len = len(dx1)
            frame_len = int(frame_len * data_fraction)
            log_mat_pos1 = dx1[:frame_len]
            matrix1 = log_mat_pos1.flatten()

            for i in range(1, n_frames):
                filename2 = "/%s/%s/%s" % (group, subgroup, frames_list[i])
                dx2 = fx[filename2] 
                log_mat_pos2 = dx2[:frame_len]
                matrix2 = log_mat_pos2.flatten()

                yield [matrix1, matrix2]

                matrix1 = matrix2


###################
# Usage with Image data, for creating tasks with two datablocks
# python source.py data/image_dataset_5.0.h5 -r redis-host -p redis-port -o stats_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="",
                                     prog="source.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(dest='filename', help='input stream file')
    parser.add_argument('-r', '--redis_host', type=str, required=True, help='Redis host')
    parser.add_argument('-p', '--redis_port', type=str, required=True, help='Redis port')
    parser.add_argument('-o', '--output_stats_dir', type=str, help='output stats directory')

    args = parser.parse_args()
    if len(args.__dict__) == 0:
        parser.print_usage()
        sys.exit(1)

    fn = transform_als_stream

    main(args.redis_host, args.redis_port, fn, args.filename,
         args.output_stats_dir)
