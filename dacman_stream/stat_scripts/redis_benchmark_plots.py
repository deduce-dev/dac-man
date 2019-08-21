import numpy as np
import matplotlib.pyplot as plt

# SET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((1*10**3)) -t set --csv -l

set_c_1_n_1_1_kb = [
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00
]

# SET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((100*10**3)) -t set --csv -l

set_c_1_n_1_100_kb = [
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    500.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00
]

# SET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((512*10**3)) -t set --csv -l

set_c_1_n_1_512_kb = [
    333.33,
    500.00,
    166.67,
    333.33,
    500.00,
    500.00,
    333.33,
    500.00,
    333.33,
    333.33,
    333.33,
    333.33,
    1000.00,
    500.00,
    333.33
]

# SET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((1*10**6)) -t set --csv -l

set_c_1_n_1_1_mb = [
    166.67,
    250.00,
    500.00,
    250.00,
    333.33,
    500.00,
    500.00,
    333.33,
    100.00,
    200.00,
    166.67,
    200.00,
    166.67,
    200.00,
    200.00
]

# SET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((1*10**7)) -t set --csv -l

set_c_1_n_1_10_mb = [
    31.25,
    55.56,
    29.41,
    37.04,
    31.25,
    22.73,
    18.52,
    12.66,
    50.00,
    27.03,
    34.48,
    31.25,
    24.39,
    31.25,
    32.26
]

# SET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((2*10**7)) -t set --csv -l

set_c_1_n_1_20_mb = [
    15.62,
    33.33,
    27.78,
    12.82,
    10.75,
    6.41,
    17.54,
    20.83,
    33.33,
    20.00,
    18.18,
    17.86,
    10.20,
    6.76,
    13.70
]

########################################################################################

# GET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((1*10**3)) -t set --csv -l

get_c_1_n_1_1_kb = [
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00
]

# GET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((100*10**3)) -t set --csv -l

get_c_1_n_1_100_kb = [
    1000.00,
    500.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    500.00,
    1000.00,
    1000.00,
    1000.00,
    1000.00,
    500.00,
    1000.00,
    1000.00,
    1000.00
]

# GET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((512*10**3)) -t set --csv -l

get_c_1_n_1_512_kb = [
    250.00,
    500.00,
    333.33,
    500.00,
    500.00,
    500.00,
    333.33,
    333.33,
    333.33,
    333.33,
    333.33,
    250.00,
    333.33,
    333.33,
    333.33
]

# GET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((1*10**6)) -t set --csv -l

get_c_1_n_1_1_mb = [
    250.00,
    250.00,
    250.00,
    200.00,
    200.00,
    200.00,
    200.00,
    200.00,
    250.00,
    200.00,
    250.00,
    200.00,
    250.00,
    250.00,
    250.00
]

# GET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((1*10**7)) -t set --csv -l

get_c_1_n_1_10_mb = [
    27.03,
    31.25,
    28.57,
    28.57,
    29.41,
    27.78,
    30.30,
    26.32,
    24.39,
    27.03,
    27.78,
    29.41,
    30.30,
    27.03,
    30.30
]

# GET: redis-benchmark -h <server> -p <port> -c 1 -n 1 -d $((2*10**7)) -t set --csv -l

get_c_1_n_1_20_mb = [
    13.16,
    13.16,
    13.89,
    12.82,
    13.51,
    12.66,
    12.82,
    12.66,
    12.99,
    12.99,
    13.70,
    11.76,
    12.50,
    11.76,
    13.51
]

##### Stat Calc

set_c_1_n_1_1_kb_avg = np.mean(set_c_1_n_1_1_kb)
set_c_1_n_1_1_kb_std = np.std(set_c_1_n_1_1_kb)

set_c_1_n_1_100_kb_avg = np.mean(set_c_1_n_1_100_kb)
set_c_1_n_1_100_kb_std = np.std(set_c_1_n_1_100_kb)

set_c_1_n_1_512_kb_avg = np.mean(set_c_1_n_1_512_kb)
set_c_1_n_1_512_kb_std = np.std(set_c_1_n_1_512_kb)

set_c_1_n_1_1_mb_avg = np.mean(set_c_1_n_1_1_mb)
set_c_1_n_1_1_mb_std = np.std(set_c_1_n_1_1_mb)

set_c_1_n_1_10_mb_avg = np.mean(set_c_1_n_1_10_mb)
set_c_1_n_1_10_mb_std = np.std(set_c_1_n_1_10_mb)

set_c_1_n_1_20_mb_avg = np.mean(set_c_1_n_1_20_mb)
set_c_1_n_1_20_mb_std = np.std(set_c_1_n_1_20_mb)

#################################################

get_c_1_n_1_1_kb_avg = np.mean(get_c_1_n_1_1_kb)
get_c_1_n_1_1_kb_std = np.std(get_c_1_n_1_1_kb)

get_c_1_n_1_100_kb_avg = np.mean(get_c_1_n_1_100_kb)
get_c_1_n_1_100_kb_std = np.std(get_c_1_n_1_100_kb)

get_c_1_n_1_512_kb_avg = np.mean(get_c_1_n_1_512_kb)
get_c_1_n_1_512_kb_std = np.std(get_c_1_n_1_512_kb)

get_c_1_n_1_1_mb_avg = np.mean(get_c_1_n_1_1_mb)
get_c_1_n_1_1_mb_std = np.std(get_c_1_n_1_1_mb)

get_c_1_n_1_10_mb_avg = np.mean(get_c_1_n_1_10_mb)
get_c_1_n_1_10_mb_std = np.std(get_c_1_n_1_10_mb)

get_c_1_n_1_20_mb_avg = np.mean(get_c_1_n_1_20_mb)
get_c_1_n_1_20_mb_std = np.std(get_c_1_n_1_20_mb)

#########

set_avg_arrs = [
    set_c_1_n_1_1_kb_avg,
    set_c_1_n_1_100_kb_avg,
    set_c_1_n_1_512_kb_avg,
    set_c_1_n_1_1_mb_avg,
    set_c_1_n_1_10_mb_avg,
    set_c_1_n_1_20_mb_avg
]

get_avg_arrs = [
    get_c_1_n_1_1_kb_avg,
    get_c_1_n_1_100_kb_avg,
    get_c_1_n_1_512_kb_avg,
    get_c_1_n_1_1_mb_avg,
    get_c_1_n_1_10_mb_avg,
    get_c_1_n_1_20_mb_avg
]


set_std_arrs = [
    set_c_1_n_1_1_kb_std,
    set_c_1_n_1_100_kb_std,
    set_c_1_n_1_512_kb_std,
    set_c_1_n_1_1_mb_std,
    set_c_1_n_1_10_mb_std,
    set_c_1_n_1_20_mb_std
]

get_std_arrs = [
    get_c_1_n_1_1_kb_std,
    get_c_1_n_1_100_kb_std,
    get_c_1_n_1_512_kb_std,
    get_c_1_n_1_1_mb_std,
    get_c_1_n_1_10_mb_std,
    get_c_1_n_1_20_mb_std
]

# Plotting

N = 6

ind = np.arange(N) 
width = 0.35

plt.figure(figsize=(10,7))

plt.bar(ind, set_avg_arrs, width, yerr=set_std_arrs, label='SET cmd')
plt.bar(ind + width, get_avg_arrs, width, yerr=get_std_arrs,
    label='GET cmd')
#plt.bar(ind + 2*width, turnaround_batch_debug, width,
#    label='Batch-Job-debug')

plt.ylabel('requests/s')


plt.xticks(ind + width / 2, ('1KB', '100KB', '512KB', '1MB', '10MB', '20MB'))
plt.legend(loc='best')

plt.title("redis-benchmark (1 client & 1 request on loop)")
#plt.show()

plt.savefig('redis_benchmark_c1_n1.png')
