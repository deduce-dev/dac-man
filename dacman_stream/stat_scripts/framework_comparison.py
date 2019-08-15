import numpy as np
import matplotlib.pyplot as plt

N = 5

#### Dacman_stream

turnaround_stream = (
    1289.37781524,
    1111.52124434,
    1137.67592572,
    1090.00554683,
    1144.4197117
#   1199.3093247413635
)

#### Batch-Job realtime

turnaround_batch_realtime = (
    1125.2202370166779,
    1763.48149316,
    1669.0116348266602,
    966.5074789524078,
    1200.8112444877625
#   1454.1191198825836
)

data_transfer_batch_realtime = (
    469.75809812545776,
    471.107903957,
    468.68610644340515,
    472.28535890579224,
    470.5160069465637
)

queue_wait_batch_realtime = (
    392.00273275375366,
    1472.73277926,
    916.9471464157104,
    212.97609519958496,
    449.44709372520447
)

processing_batch_realtime = (
    263.45940613746643,
    280.121257544,
    283.37838196754456,
    281.24602484703064,
    280.84814381599426
)

#### Batch-Job Debug

turnaround_batch_debug = (
    923.179744720459,
    1023.6603457927704,
    1046.5790665149689,
    1019.3264331817627,
    1389.8539154529572
#   1454.1191198825836
)

data_transfer_batch_debug = (
    477.9323160648346,
    468.9869227409363,
    467.7034423351288,
    469.80884766578674,
    468.4017457962036
)

queue_wait_batch_debug = (
    31.935179948806763,
    201.14211797714233,
    195.86063027381897,
    194.19256019592285,
    552.5242898464203,
)

processing_batch_debug = (
    413.3122487068176,
    353.5313050746918,
    383.0149939060211,
    355.3250253200531,
    368.92787981033325
)

#### Plotting

ind = np.arange(N) 
width = 0.25

plt.figure(figsize=(10,7))

plt.bar(ind, turnaround_stream, width, label='DacMan-Stream')
plt.bar(ind + width, turnaround_batch_realtime, width,
    label='Batch-Job-realtime')
plt.bar(ind + 2*width, turnaround_batch_debug, width,
    label='Batch-Job-debug')

plt.ylabel('Turnaround Time (s)')


plt.xticks(ind + width, ('32', '64', '128', '192', '256'))
plt.legend(loc='best')
#plt.show()

plt.savefig('turnaround_comparison_bar.png')
plt.clf()


ind = np.arange(N) 
width = 0.25

plt.figure(figsize=(10,7))

plt.bar(ind, turnaround_stream, width, label='DacMan-Stream')

bar_d_and_p = np.add(data_transfer_batch_realtime, processing_batch_realtime).tolist()
plt.bar(ind + width, data_transfer_batch_realtime, width,
    label='Batch-Job-realtime-DataTransfer-T')
plt.bar(ind + width, processing_batch_realtime, width,
    bottom=data_transfer_batch_realtime, label='Batch-Job-realtime-Process-T')
plt.bar(ind + width, queue_wait_batch_realtime, width,
    bottom=bar_d_and_p, label='Batch-Job-realtime-Queue-T')

bar_d_and_p = np.add(data_transfer_batch_debug, processing_batch_debug).tolist()
plt.bar(ind + 2*width, data_transfer_batch_debug, width,
    label='Batch-Job-debug-DataTransfer-T')
plt.bar(ind + 2*width, processing_batch_debug, width,
    bottom=data_transfer_batch_debug, label='Batch-Job-debug-Process-T')
plt.bar(ind + 2*width, queue_wait_batch_debug, width,
    bottom=bar_d_and_p, label='Batch-Job-debug-Queue-T')

plt.ylabel('Turnaround Time (s)')
plt.xlabel('# of Cores')

plt.xticks(ind + width, ('32', '64', '128', '192', '256'))
plt.legend(loc='best')
#plt.show()

plt.savefig('turnaround_comparison_stacked_bar.png')

