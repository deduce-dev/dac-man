import os
import sys
import h5py
import redis
import copy
import uuid
import numpy as np
from datetime import datetime
from hashlib import blake2b
from math import sqrt
from scipy import stats
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

import settings as _settings

r = redis.Redis(
    host=_settings.HOST,
    port=_settings.PORT,
    db=_settings.DATABASE
)

startTime = datetime.now()


if __name__ == "__main__":

    hash_job_ordered_list = blake2b(digest_size=20)
    hash_job_ordered_list.update(_settings.JOB_ORDERED__LIST.encode('utf-8'))
    job_ordered_list_hash_string = "%s:%s" % (_settings.JOB_ORDERED__LIST, hash_job_ordered_list.hexdigest())

    results_keys = r.lrange(job_ordered_list_hash_string, 0, -1)

    results_values = r.mget(results_keys)

    results_values = map(lambda x: eval(x), results_values)

    #(type(results_values))

    i = 1
    for result in zip(*results_values):
        print(np.array(result))
        plt.figure()
        plt.plot(np.array(result))
        plt.ylabel('Value')
        plt.xlabel('Frame number')
        savestr = str("plot_") + str(i) + '.png'
        plt.savefig(savestr)
        plt.close("all")
        i += 1

    #rms_list, t_test_t, t_test_p = zip(*results_values)

    '''
    #rms_list = np.array(rms_list)
    #t_test_t = np.array(t_test_t)
    #t_test_p = np.array(t_test_p)


    #print(results_keys)
    #print(list(results_values))
    #print(eval(*results_values, {}))
    #print(eval(*results_values))
    #print(eval(str(results_values)))
    #print(zip(*results_values))
    print(rms_list)
    #print(t_test_t)
    #print(t_test_p)

    plt.figure()
    plt.plot(rms_list)
    plt.ylabel('RMSE value')
    plt.xlabel('Frame number')
    savestr = 'rmse.png'
    plt.savefig(savestr)
    plt.close("all")
    #print(results_values)
    '''
