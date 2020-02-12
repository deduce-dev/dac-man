# def put(self, k, datablock, window_size=1):
#     datahash = blake2b(digest_size=20)
#     datahash.update(datablock)
#     datablock_id = "%s:%s" % (_settings.DATABLOCK_PREFIX, datahash.hexdigest())
#
#     self._redis.set(datablock_id, datablock.tostring())
#
#     datablock_ids = self._redis.get(k)
#     datablock_ids.append(datablock_id)
#
#     # if enough data blocks are available, then time to set up a task
#     if len(datablock_ids) == window_size:
#         task_uuid = "%s:%s" % (_settings.TASK_PREFIX, str(uuid.uuid4()))
#         self._redis.rpush(self._task_list, task_uuid)
#         self._redis.lpush(self._task_q, (task_uuid, *datablock_ids, "custom"))

from cache import Cache
import pandas as pd
import argparse
import sys


def send(cache, k, datablock, window_size):
    datablock_id = cache.put_datablock(datablock)
    cache.assign_datablock_to_window(k, datablock_id)
    n_datablocks = cache.get_current_window_size(k)
    if n_datablocks == window_size:
        datablock_ids = cache.get_windowed_datablocks(k)
        cache.create_task(*datablock_ids)


def get_window_key(row, key_name):
    window_key = row[key_name]
    return window_key


def main(stream_src, measurement, window_size, key_name):
    cache = Cache()
    df = pd.read_csv(stream_src, comment='#', sep=',', na_filter=False, dtype='str')
    #m_series = df[measurement]
    #for m in m_series.values:
    for index, row in df.head().iterrows():
        window_key = get_window_key(row, key_name)
        print(window_key, row[measurement])
        send(cache, window_key, row[measurement], window_size)


###################
def transform_fluxnet_stream(stream_src):
    df = pd.read_csv(stream_src, comment='#', sep=',', na_filter=False, dtype='str')
    df['datetime'] = pd.to_datetime(df['TIMESTAMP_END'], format="%Y%m%d%H%M",errors='coerce')
    for index, row in df.head().iterrows():
        yield row


def transform_lathuile_stream(stream_src):
    df = pd.read_csv(stream_src, comment='#', sep=',', na_filter=False, dtype='str')
    df['datetime'] = pd.to_datetime(df['Year'].str[:-2]) + pd.to_timedelta(df['DoY'].str[:-2] + 'days') + \
        pd.to_timedelta('-1 day') + pd.to_timedelta(pd.to_numeric(df['Time']), unit='h')
    for index, row in df.head().iterrows():
        yield row


###################
def _fluxnetClientParser(subparsers):
    parser_worker = subparsers.add_parser('fluxnet',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Streaming dstream for Fluxnet data """)

    parser_worker.add_argument(dest='filename', help='input stream file')
    parser_worker.add_argument('-m', '--measurement',
                               choices=['CO2_F_MDS', 'WD', 'TA_F'], type=str,
                               default='CO2_F_MDS', help='measurement')
    parser_worker.add_argument('-k', '--keyname', type=str, help='key name', default='TIMESTAMP_START')
    parser_worker.add_argument('-s', '--windowsize', type=int, help='window size', default=1)


def _lathuileClientParser(subparsers):
    parser_worker = subparsers.add_parser('lathuile',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Streaming dstream for La Thuile data """)

    parser_worker.add_argument(dest='filename', help='input stream file')
    parser_worker.add_argument('-m', '--measurement',
                               choices=['CO2_F_MDS', 'WD', 'TA_F'], type=str,
                               default='CO2_F_MDS', help='measurement')
    parser_worker.add_argument('-k', '--keyname', type=str, help='key name', default='TIMESTAMP_START')
    parser_worker.add_argument('-s', '--windowsize', type=int, help='window size', default=1)


###################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="",
                                     prog="dstream",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(dest='filename', help='input stream file')
    parser.add_argument('-m', '--measurement',
                        choices=['CO2_F_MDS', 'WD', 'TA_F'], type=str,
                        default='CO2_F_MDS', help='measurement')
    parser.add_argument('-k', '--keyname', type=str, help='key name', default='TIMESTAMP_START')
    parser.add_argument('-s', '--windowsize', type=int, help='window size', default=1)

    args = parser.parse_args()
    if len(args.__dict__) == 0:
        parser.print_usage()
        sys.exit(1)

    main(args.filename, args.measurement, args.windowsize)
    # python dstream.py data/fluxnet2015/FLX_AT-Neu_FLUXNET2015_FULLSET_HH_2002-2012_1-3.csv -s 2
