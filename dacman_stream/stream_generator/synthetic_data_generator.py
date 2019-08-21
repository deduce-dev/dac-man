import os
import sys
import csv
import uuid
import time
import redis
import numpy as np
from hashlib import blake2b

r = None

script_start = time.time()

#### I want to calculate how heavy is the INFO command in Redis
redis_size_request_start = []
redis_size_request_end = []

data_hashing_start = []
data_hashing_end = []

data_send_start = {}
data_send_end = {}

def write_dict_to_csv(dict_or_arr, output_dir_path, name, arr=False):
    output_full_path = os.path.join(output_dir_path, name)

    with open(output_full_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
    if arr:
        for value in dict_or_arr:
           writer.writerow(value)
    else:
        for key, value in dict_or_arr.items():
           writer.writerow([key, value])

def calc_stats():
    d1 = data_send_start
    data_send_start_sorted = [(k, d1[k]) for k in sorted(d1, key=d1.get)]

    total_sum = 0

    diff_sum = 0
    for k, v in data_send_start_sorted:
        send_start = data_send_start[k]
        send_end = data_send_start[k]

        diff = send_end - send_start
        diff_sum += diff

    total_sum += diff_sum
    print("Sending to Redis total time:", diff_sum)

    diff_sum = 0
    for hash_start, hash_end in zip(data_hashing_start, data_hashing_end):
        diff = hash_end - hash_start
        diff_sum += diff

    total_sum += diff_sum
    print("Hashing total time:", diff_sum)

    diff_sum = 0
    for r_req_start, r_req_end in zip(redis_size_request_start, redis_size_request_end):
        diff = r_req_end - r_req_start
        diff_sum += diff

    total_sum += diff_sum
    print("Requesting Redis info (memory size):", diff_sum)

    return total_sum


def publish_tasks(r, task_queue_hs, data_a, data_b):
    data_hash_start_t = time.time()

    hash1 = blake2b(digest_size=20)
    hash2 = blake2b(digest_size=20)

    hash1.update(data_a)
    hash2.update(data_b)

    hash1_string = "%s:%s" % ('datablock', hash1.hexdigest())
    hash2_string = "%s:%s" % ('datablock', hash2.hexdigest())

    task_uuid = "%s:%s" % ('task', str(uuid.uuid4()))

    data_hash_end_t = time.time()

    data_hashing_start.append(data_hash_start_t)
    data_hashing_end.append(data_hash_end_t)

    ##### Collecting Stats #####
    data_send_start[task_uuid] = time.time()
    ############################

    r.set(hash1_string, data_a.tostring())
    r.set(hash2_string, data_b.tostring())

    #### Adding the task to the ordered job list

    r.lpush(task_queue_hs, (task_uuid, hash1_string, hash2_string, "custom"))

    ##### Collecting Stats #####
    data_send_end[task_uuid] = time.time()
    ############################

    print("Pushed", task_uuid, "To", task_queue_hs)


def generate(number_of_bytes):
    data_a = np.random.bytes(number_of_bytes)
    data_b = np.random.bytes(number_of_bytes)

    return data_a, data_b


def generate_sample():
    a = np.random.random_sample()
    b = np.random.random_sample()

    return np.float32(a), np.float32(b)


def s_main(args):
    # level: 3 -- 8 Bytes -- 2**3
    # level: 4 -- 16 Bytes -- 2**4
    # level: 5 -- 32 Bytes -- 2**5
    # level: 6 -- 64 Bytes -- 2**6
    # level: 7 -- 128 Bytes -- 2**7
    # level: 8 -- 256 Bytes -- 2**8
    # level: 9 -- 512 Bytes -- 2**9
    # level: 10 -- 1024 Bytes / 1 KB -- 2**10
    # level: 13 -- 8 KB -- 2**13
    # level: 14 -- 16 KB -- 2**14
    # level: 15 -- 32 KB -- 2**15
    # level: 16 -- 64 KB -- 2**16
    # level: 17 -- 128 KB -- 2**17
    # level: 18 -- 256 KB -- 2**18
    # level: 19 -- 512 KB -- 2**19
    # level: 20 -- 1024 KB / 1 MB -- 2**20
    # level: 21 -- 2 MB -- 2**21
    # level: 22 -- 4 MB -- 2**22
    # level: 23 -- 8 MB -- 2**23
    # level: 24 -- 16 MB -- 2**24

    task_queue = args['task_queue']
    level = args['level']
    output_dir = args['output_dir']

    r = redis.Redis(
        host=args['redis_server'],
        port=args['redis_port']
    )

    redis_size_t_start = time.time()
    redis_used_size = r.info('memory')
    redis_used_size = int(redis_used_size['used_memory'])
    redis_size_t_end = time.time()

    redis_size_request_start.append(redis_size_t_start)
    redis_size_request_end.append(redis_size_t_end)

    job_count = 0
    while redis_used_size < (2**20 * 1):
        #data_a, data_b = generate(2**level)
        data_a, data_b = generate_sample()

        publish_tasks(r, task_queue, data_a, data_b)

        job_count += 1

        redis_size_t_start = time.time()
        redis_used_size = r.info('memory')
        redis_used_size = int(redis_used_size['used_memory'])
        redis_size_t_end = time.time()

        print("redis_used_size: %f GB" % float(redis_used_size)/(10**6))

        redis_size_request_start.append(redis_size_t_start)
        redis_size_request_end.append(redis_size_t_end)

    script_end = time.time()

    script_time = script_end-script_start
    print("Script total time:", script_time)

    write_dict_to_csv(data_send_start, output_dir, "data_send_start.csv", arr=False)
    write_dict_to_csv(data_send_end, output_dir, "data_send_end.csv", arr=False)
    write_dict_to_csv(data_hashing_start, output_dir, "data_hashing_start.csv", arr=True)
    write_dict_to_csv(data_hashing_end, output_dir, "data_hashing_end.csv", arr=True)
    write_dict_to_csv(redis_size_request_start, output_dir, "redis_size_request_start.csv", arr=True)
    write_dict_to_csv(redis_size_request_end, output_dir, "redis_size_request_end.csv", arr=True)

    utilized_time = calc_stats()

    not_utilized_time = script_time - utilized_time

    print("Not Utilized time:", not_utilized_time)


if __name__ == '__main__':
    if (len(sys.argv) < 6):
            print("Usage: python synthetic_data_generator.py <redis_server> <redis_port> <task_queue> <output_dir> <level>")
    else:
        args = {
            'redis_server': sys.argv[1],
            'redis_port': sys.argv[2],
            'task_queue': sys.argv[3],
            'output_dir': sys.argv[4],
            'level': sys.argv[5],
        }
        s_main(args)
