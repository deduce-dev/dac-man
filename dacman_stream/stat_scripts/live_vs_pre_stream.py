import os
import sys
import numpy as np
import matplotlib.pyplot as plt

font = {
    'size': 22,
}
label_size = 20
label_pad_y = 15
label_pad_x = 10
graph_ext = "pdf"
#graph_ext = "png"

######################################################################################
######################################################################################

live_stream_avg_tput = [
]


pre_stream_avg_tput = [
    492.14950634696754,
    1932.7928928373126,
    1669.6057745696835,
    1431.1666666666667,
    1386.5222222222221,
    1230.1832315380345
]

N = 1

fig, ax = plt.subplots(figsize=(9,5))

ind = np.arange(N)    # the x locations for the groups
width = 0.35         # the width of the bars

p1 = ax.bar(ind, live_stream_avg_tput, width, yerr=non_pipelined_std_tput, color='b')
p2 = ax.bar(ind + width, pre_stream_avg_tput, width, yerr=pipelined_std_tput, color='r')

#ax.set_title('Scores by group and gender')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(('64'))

ax.set_ylabel("Avg Throughput (tasks/s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Number of DacMan-instances", fontdict=font, labelpad=label_pad_x)

ax.legend((p1[0], p2[0]), ('live-stream', 'pre-stream'))
ax.autoscale_view()

plt.tight_layout()

output_dir = sys.argv[1]

graph_filename = "pipeline_vs_non_pipeline_blot_avg_tput." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename))


