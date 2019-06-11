import sys
import time
import redis
import numpy as np

def get_redis_instance(host, port, db):
    '''
    Return a redis instance with the given config
    '''
    r = redis.Redis(
        host=host,
        port=port,
        db=db
    )

    return r

def s_main(args):
    host = args['r_host']
    port = args['r_port']
    db =  args['r_db']

    r = get_redis_instance(host, port, db)

    data_id1 = "datablock:a1469bf2c3969c080b64f3fca524ff87b8f4dfb7"
    data_id2 = "datablock:6f4f31413dba0e5ebc03ffbddda6788b6ee28e8b"

    start = float(time.time())
    data1 = r.get(data_id1)
    data2 = r.get(data_id2)
    end = float(time.time())

    print(end - start)

    start = float(time.time())
    data1 = np.fromstring(r.get(data_id1), dtype='<f4')
    data2 = np.fromstring(r.get(data_id2), dtype='<f4')
    end = float(time.time())

    print(end - start)


if __name__ == '__main__':
    args = {
        'r_host': sys.argv[1],
        'r_port': sys.argv[2],
        'r_db': sys.argv[3],
        'redis_queue_id': sys.argv[4],
    }

    s_main(args)