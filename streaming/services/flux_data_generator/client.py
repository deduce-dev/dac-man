from cache import Cache
import pandas as pd
import argparse
import sys
import os
import socket


# Pushing data blocks to Cache; if window-size is matched, then create a task
def send_windowed_srcs(cache, k, datablock, window_size):
    datablock_id = cache.put_datablock(datablock)
    cache.assign_datablock_to_window(k, datablock_id)
    n_datablocks = cache.get_current_window_size(k)
    if n_datablocks == window_size:
        datablock_ids = cache.get_windowed_datablocks(k)
        cache.create_task(*datablock_ids)


def send_independent_srcs(cache, datablockA, datablockB):
    datablockA_id = cache.put_datablock(datablockA)
    datablockB_id = cache.put_datablock(datablockB)
    cache.create_task(*[datablockA_id, datablockB_id])


def get_window_key(row, key_name):
    window_key = row[key_name]
    return window_key


def main(stream_transformer, stream_src, measurement, window_size, key_name,
            stats_dir, is_independent=True, host=None, port=None):
    cache = Cache(host, port)
    print("Streaming data...")
    stream_gen = stream_transformer(stream_src)

    if is_independent:
        row1 = next(stream_gen)
        while True:
            try:
                row2 = next(stream_gen)
                send_independent_srcs(cache, row1[measurement], row2[measurement])
                row1 = row2
            except StopIteration:
                break
    else:
        for row in stream_gen:
            window_key = get_window_key(row, key_name)
            send_windowed_srcs(cache, window_key, row[measurement], window_size)

    cache.write_stats(stats_dir)


###################
# Data stream transformation
def transform_fluxnet_stream(stream_src):
    df = pd.read_csv(stream_src, comment='#', sep=',', na_filter=False, dtype='str')
    df['datetime'] = df['TIMESTAMP_END']
    for index, row in df.iterrows():
        yield row


def transform_lathuile_stream(stream_src):
    df = pd.read_csv(stream_src, comment='#', sep=',', na_filter=False, dtype='str')
    df['datetime'] = (pd.to_datetime(df['Year'].str[:-2]) + pd.to_timedelta(df['DoY'].str[:-2] + 'days') + \
        pd.to_timedelta('-1 day') + pd.to_timedelta(pd.to_numeric(df['Time']), unit='h'))
    df['datetime'] = df['datetime'].dt.strftime('%Y%m%d%H%M')
    for index, row in df.iterrows():
        yield row


###################
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def _fluxnetClientParser(subparsers):
    parser_worker = subparsers.add_parser('fluxnet',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Streaming dstream for Fluxnet data """)

    parser_worker.set_defaults(action="fluxnet")
    parser_worker.add_argument(dest='filename', help='input stream file')
    parser_worker.add_argument('-m', '--measurement',
                               choices=['CO2_F_MDS', 'WD', 'TA_F'], type=str,
                               default='CO2_F_MDS', help='measurement')
    parser_worker.add_argument('-r', '--redis_host', type=str, required=True, help='Redis host')
    parser_worker.add_argument('-p', '--redis_port', type=str, required=True, help='Redis port')
    parser_worker.add_argument('-k', '--keyname', type=str, help='key name', default='datetime')
    parser_worker.add_argument('-s', '--windowsize', type=int, help='window size', default=1)
    parser_worker.add_argument('-o', '--output_stats_dir', type=str, help='output stats directory')
    parser_worker.add_argument('-i', '--independent', 
        type=str2bool, nargs='?', const=True, default=False,
        help='independent source or not')


def _lathuileClientParser(subparsers):
    parser_worker = subparsers.add_parser('lathuile',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Streaming dstream for La Thuile data """)

    parser_worker.set_defaults(action="lathuile")
    parser_worker.add_argument(dest='filename', help='input stream file')
    parser_worker.add_argument('-m', '--measurement',
                               choices=['CO2', 'WD', 'Ta_f'], type=str,
                               default='CO2', help='measurement')
    parser_worker.add_argument('-r', '--redis_host', type=str, required=True, help='Redis host')
    parser_worker.add_argument('-p', '--redis_port', type=str, required=True, help='Redis port')
    parser_worker.add_argument('-k', '--keyname', type=str, help='key name', default='datetime')
    parser_worker.add_argument('-s', '--windowsize', type=int, help='window size', default=1)
    parser_worker.add_argument('-o', '--output_stats_dir', type=str, help='output stats directory')
    parser_worker.add_argument('-i', '--independent', 
        type=str2bool, nargs='?', const=True, default=False,
        help='independent source or not')


###################
# Usage with Ameriflux data, for creating tasks with two datablocks
# python client.py fluxnet data/fluxnet2015/FLX_AT-Neu_FLUXNET2015_FULLSET_HH_2002-2012_1-3.csv -s 2
# python client.py lathuile data/la_thuile/AT-Neu.2002.synth.hourly.allvars.csv -s 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="",
                                     prog="dstream",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers()
    _fluxnetClientParser(subparsers)
    _lathuileClientParser(subparsers)

    args = parser.parse_args()
    if len(args.__dict__) == 0:
        parser.print_usage()
        sys.exit(1)

    if args.action == 'fluxnet':
        fn = transform_fluxnet_stream
    else:
        fn = transform_lathuile_stream

    main(fn, args.filename, args.measurement, args.windowsize, args.keyname,
        args.output_stats_dir, is_independent=args.independent, host=args.redis_host,
        port=args.redis_port)
