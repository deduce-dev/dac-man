import numpy as np
import matplotlib.pyplot as plt

N = 5
'''
turnaround_stream = (
    1199.1213681697845,
    1198.9609155654907,
    1199.110425710678,
    1199.7327718734741,
    1200.4962775707245
#   1199.3093247413635
)
'''

turnaround_stream = (
    1289.37781524,
    1111.52124434,
    1137.67592572,
    1090.00554683,
    1144.4197117
#   1199.3093247413635
)

turnaround_batch_realtime = (
    1125.2202370166779,
    1763.48149316,
    1669.0116348266602,
    966.5074789524078,
    1200.8112444877625
#   1454.1191198825836
)

turnaround_batch_debug = (
    923.179744720459,
    1023.6603457927704,
    1046.5790665149689,
    1019.3264331817627,
    1389.8539154529572
#   1454.1191198825836
)

ind = np.arange(N) 
width = 0.25
plt.bar(ind, turnaround_stream, width, label='DacMan-Stream')
plt.bar(ind + width, turnaround_batch_realtime, width,
    label='Batch-Job-realtime')
plt.bar(ind + 2*width, turnaround_batch_debug, width,
    label='Batch-Job-debug')

plt.ylabel('Turnaround Time (s)')

plt.xticks(ind + width, ('N1', 'N2', 'N4', 'N6', 'N8'))
plt.legend(loc='best')
#plt.show()

plt.savefig('turnaround_comparison_bar.png')