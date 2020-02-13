import os
import sys
import numpy as np
import matplotlib.pyplot as plt

font = {
    'size': 22,
}
label_size = 20
label_pad_y = 10
label_pad_x = 10
graph_ext = "pdf"
#graph_ext = "png"

######################################################################################
######################################################################################
######################################################################################
######################################################################################

non_pipelined_avg_tput = [
    466.5236470014627,
    527.6477777777778,
    518.5288888888889,
    536.6690727373681,
    531.0333333333333,
    494.64519711271515
]

non_pipelined_std_tput = [
    111.45002707018347,
    29.851267338731116,
    31.224460655227922,
    26.06493372949297,
    16.765805146852394,
    24.448614437077026
]


pipelined_avg_tput = [
    492.14950634696754,
    1932.7928928373126,
    1669.6057745696835,
    1431.1666666666667,
    1386.5222222222221,
    1230.1832315380345
]

pipelined_std_tput = [
    38.97670911937093,
    74.9056180114484,
    70.76172411043116,
    42.020841389852144,
    47.497257880564426,
    239.29983182897826
]

N = 6

fig, ax = plt.subplots(figsize=(9,5))

ind = np.arange(N)    # the x locations for the groups
width = 0.35         # the width of the bars

p1 = ax.bar(ind, non_pipelined_avg_tput, width, yerr=non_pipelined_std_tput, color='b')
p2 = ax.bar(ind + width, pipelined_avg_tput, width, yerr=pipelined_std_tput, color='r')

#ax.set_title('Scores by group and gender')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(('1', '4', '8', '16', '32', '64'))

ax.set_ylabel("Avg Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Number of DacMan-instances", fontdict=font, labelpad=label_pad_x)

ax.legend((p1[0], p2[0]), ('default', 'pipeline'), fontsize=label_size)
ax.autoscale_view()

#plt.tight_layout(pad=1.08, w_pad=2.08)
plt.tick_params(labelsize=label_size)

output_dir = sys.argv[1]

graph_filename = "pipeline_vs_non_pipeline_blot_avg_tput." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename), bbox_inches='tight')

plt.clf()

######################################################################################
######################################################################################
######################################################################################
######################################################################################

non_pipelined_avg_tput = [
    487.7992224382116, 486.16828658705913, 484.7117467370175
]

non_pipelined_std_tput = [
    29.895029896336744, 28.051535557499186, 37.305648521152044
]


pipelined_avg_tput = [
    1653.5462371563456, 1617.434046098306, 1608.1755068036657
]

pipelined_std_tput = [
    86.31004693563175, 66.86019472731758, 67.09964960316529
]


N = 3

fig, ax = plt.subplots(figsize=(9,5))

ind = np.arange(N)    # the x locations for the groups
width = 0.35         # the width of the bars

p1 = ax.bar(ind, non_pipelined_avg_tput, width, yerr=non_pipelined_std_tput, color='b')
p2 = ax.bar(ind + width, pipelined_avg_tput, width, yerr=pipelined_std_tput, color='r')

#ax.set_title('Scores by group and gender')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(('64', '128', '256'))

ax.set_ylim(top=2500)
ax.set_ylabel("Avg Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Number of DacMan-instances", fontdict=font, labelpad=label_pad_x)

ax.legend((p1[0], p2[0]), ('default', 'pipeline'), loc='best', fontsize=label_size)
ax.autoscale_view()

plt.tight_layout(pad=1.08, w_pad=2.08)
plt.tick_params(labelsize=label_size)

output_dir = sys.argv[1]

graph_filename = "pipeline_vs_non_pipeline_cori_avg_tput." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename), bbox_inches='tight')

plt.clf()