import os
import sys
import numpy as np
import matplotlib.pyplot as plt

'''
font = {
    'size': 22,
}
label_size = 20
label_pad_y = 10
label_pad_x = 10
graph_ext = "pdf"
#graph_ext = "png"
'''

font = {
    'size': 28,
}
label_size = 28
label_pad_y = 15
label_pad_x = 10
graph_ext = "pdf"
#graph_ext = "png"

######################################################################################
######################################################################################
######################################################################################
######################################################################################

non_pipelined_avg_tput = [
    1267.6385542168675, 1252.547619047619, 1156.1978021978023
]

non_pipelined_std_tput = [
    175.34850519068735, 165.9158137617865, 279.6034955440371
]


pipelined_avg_tput = [
    1169.0444444444445, 1169.0444444444445, 1169.0444444444445
]

pipelined_std_tput = [
    244.80068587009544, 224.52552001009255, 249.37182907418082
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

graph_filename = "pipeline_vs_non_pipeline_cori_avg_tput_flux_msip." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename), bbox_inches='tight')

plt.clf()