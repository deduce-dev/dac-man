import os
import sys
import numpy as np
import matplotlib.pyplot as plt

font = {
    'size': 28,
}
font_bar_t = {
    'size': 18,
}
label_size = 28
legend_size = 15
label_pad_y = 15
label_pad_x = 10
figsize1 = 9
figsize2 = 5
graph_ext = "pdf"
#graph_ext = "png"
is_log = False

output_dir = sys.argv[1]

###################################################################################
############################# Live Stream #########################################
###################################################################################

# ALS local, cluster
als_avg_tput = [1.0013351134846462, 1.2057142857142857]
als_std_tput = [0.036514804622636426, 0.40422260991605474]
als_max_tput = [2, 2]

als_avg_etime_latency = [1407.272140381972, 1116.0575703516956]
als_std_etime_latency = [741.4247521398222, 597.1383297818041]
als_max_etime_latency = [2428.00346159935, 1954.7415826320648]

als_runtime = [3518.1820373535156, 3153.8903996944427]

# Scenario A local, cluster
fluxnet_msip_norm_tput = [1360.8728958111233, 85.24734454115277]
fluxnet_msip_avg_tput = [1348.8974358974358, 88.86317567567568]
fluxnet_msip_std_tput = [186.09127824693778, 4.899999522498896]
fluxnet_msip_max_tput = [1548, 94]

fluxnet_msip_avg_etime_latency = [4.66021491109057, 550.9495166040621]
fluxnet_msip_std_etime_latency = [2.8641684508145238, 323.86825216564495]
fluxnet_msip_max_etime_latency = [10.389662981033325, 1148.3067152500153]

fluxnet_msip_runtime = [77.31427597999573, 1234.2290258407593]

# Scenario B local, cluster
fluxnet_mscp_norm_tput = [439.96169778427316, 92.22906104508462]
fluxnet_mscp_avg_tput = [434.7603305785124, 91.97202797202797]
fluxnet_mscp_std_tput = [71.99816627524729, 4.468528732612402]
fluxnet_mscp_max_tput = [561, 95]

fluxnet_mscp_avg_etime_latency = [0.0006332642106698438, 210.22524331855857]
fluxnet_mscp_std_etime_latency = [0.0001827606526517467, 120.46637411282437]
fluxnet_mscp_max_etime_latency = [0.00813746452331543, 415.688595533371]

fluxnet_mscp_runtime = [119.5704128742218, 570.4147644042969]

N = 2

ind = np.arange(N)    # the x locations for the groups
width = 0.25         # the width of the bars
bar_label_diff = 0.1

fig, ax = plt.subplots(figsize=(figsize1,figsize2))

p1 = ax.bar(ind, als_avg_tput, width, yerr=als_std_tput, color='b', log=is_log)
p2 = ax.bar(ind + width, fluxnet_msip_norm_tput, width, color='r', log=is_log)
p3 = ax.bar(ind + 2*width, fluxnet_mscp_norm_tput, width, color='g', log=is_log)

#p2 = ax.bar(ind + width, fluxnet_msip_avg_tput, width, yerr=fluxnet_msip_std_tput, color='r', log=is_log)
#p3 = ax.bar(ind + 2*width, fluxnet_mscp_avg_tput, width, yerr=fluxnet_mscp_std_tput, color='g', log=is_log)

for i, v in enumerate(als_avg_tput):
    ax.text(i, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')
    #ax.text(v + 3, i + .25, str(v), fontdict=font)

#for i, v in enumerate(fluxnet_msip_avg_tput):
for i, v in enumerate(fluxnet_msip_norm_tput):
    ax.text(i + width, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')

#for i, v in enumerate(fluxnet_mscp_avg_tput):
for i, v in enumerate(fluxnet_mscp_norm_tput):
    ax.text(i + 2*width, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')

#ax.set_xticks(ind + width / 2)
ax.set_xticks(ind + width)

ax.set_xticklabels(('Local', 'Cluster'))
ax.tick_params(labelsize=label_size)

ax.set_ylabel("Avg Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Configuration Mode", fontdict=font, labelpad=label_pad_x)

ax.legend((p1[0], p2[0], p3[0]), ('ALS-SS', 'FLUX-MSIP', 'FLUX-MSCP'), fontsize=legend_size)
#ax.set_yscale('log')

#fig.canvas.draw()
ax.relim()
ax.autoscale_view()
ax.set_ylim(top=1600)
plt.tight_layout()

graph_filename = "avg_tput_modes_1_worker_live_stream." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename))

plt.clf()

###########################################################################

fig, ax = plt.subplots(figsize=(figsize1,figsize2))

p1 = ax.bar(ind, als_avg_etime_latency, width, yerr=als_std_etime_latency, color='b', log=is_log)
p2 = ax.bar(ind + width, fluxnet_msip_avg_etime_latency, width, yerr=fluxnet_msip_std_etime_latency, color='r', log=is_log)
p3 = ax.bar(ind + 2*width, fluxnet_mscp_avg_etime_latency, width, yerr=fluxnet_mscp_std_etime_latency, color='g', log=is_log)

for i, v in enumerate(als_avg_etime_latency):
    ax.text(i, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')
    #ax.text(v + 3, i + .25, str(v), fontdict=font)

for i, v in enumerate(fluxnet_msip_avg_etime_latency):
    ax.text(i + width, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')

for i, v in enumerate(fluxnet_mscp_avg_etime_latency):
    if v < 1:
        ax.text(i + 2*width, v, "%.1e" % v, fontdict=font_bar_t,
            horizontalalignment='center', verticalalignment='bottom')
    else:
        ax.text(i + 2*width, v, "%.1f" % v, fontdict=font_bar_t,
            horizontalalignment='center', verticalalignment='bottom')

#ax.set_xticks(ind + width / 2)
ax.set_xticks(ind + width)

ax.set_xticklabels(('Local', 'Cluster'))
ax.tick_params(labelsize=label_size)

ax.set_ylabel("Avg Latency (s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Configuration Mode", fontdict=font, labelpad=label_pad_x)

ax.legend((p1[0], p2[0], p3[0]), ('ALS-SS', 'FLUX-MSIP', 'FLUX-MSCP'),
    fontsize=legend_size, ncol=3)
#ax.set_yscale('log')

ax.relim()
ax.autoscale_view()
ax.set_ylim(top=2200)
plt.tight_layout()

graph_filename = "et_latency_modes_1_worker_live_stream." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename))

plt.clf()

########################################################################
######################### Buffered #####################################
########################################################################

# ALS local, cluster
als_avg_tput = [1.0013351134846462, 1.267962806424345]
als_std_tput = [0.036514804622636426, 0.44289811559492326]
als_max_tput = [2, 2]

als_avg_etime_latency = [1407.272140381972, 1480.3568764973481]
als_std_etime_latency = [741.4247521398222, 512.4189727455707]
als_max_etime_latency = [2428.00346159935, 2452.443650484085]

als_runtime = [3518.1820373535156, 3047.510125875473]

# Scenario A local, cluster
fluxnet_msip_norm_tput = [1099.0267370221893, 88.86012207832023]
fluxnet_msip_avg_tput = [1095.9791666666667, 88.78818565400844]
fluxnet_msip_std_tput = [220.62567181987734, 2.592725070351098]
fluxnet_msip_max_tput = [1546, 92]

fluxnet_msip_avg_etime_latency = [94.01350549280191, 690.4128863324522]
fluxnet_msip_std_etime_latency = [3.342196346270228, 316.78707715894865]
fluxnet_msip_max_etime_latency = [100.53842282295227, 1238.4592454433441]

fluxnet_msip_runtime = [188.87028050422668, 1325.895758152008]

# Scenario B local, cluster
#fluxnet_mscp_norm_tput = [1213.8846366714545, 87.82780249396623]
fluxnet_mscp_norm_tput = [1213.8846366714545, 89.13882552567513]
fluxnet_mscp_avg_tput = [1195.590909090909, 89.01522842639594]
fluxnet_mscp_std_tput = [179.39194242848384, 2.610295554822017]
fluxnet_mscp_max_tput = [1550, 91]

fluxnet_mscp_avg_etime_latency = [106.64605202725807, 381.9769882241495]
fluxnet_mscp_std_etime_latency = [31.683311079651013, 127.14768509581675]
fluxnet_mscp_max_etime_latency = [154.90666460990906, 598.220730304718]

fluxnet_mscp_runtime = [198.24356698989868, 748.4115269184113]

N = 2

ind = np.arange(N)    # the x locations for the groups
width = 0.25         # the width of the bars
bar_label_diff = 0.1

fig, ax = plt.subplots(figsize=(figsize1,figsize2))

p1 = ax.bar(ind, als_avg_tput, width, yerr=als_std_tput, color='b', log=is_log)
p2 = ax.bar(ind + width, fluxnet_msip_norm_tput, width, color='r', log=is_log)
p3 = ax.bar(ind + 2*width, fluxnet_mscp_norm_tput, width, color='g', log=is_log)

#p2 = ax.bar(ind + width, fluxnet_msip_avg_tput, width, yerr=fluxnet_msip_std_tput, color='r', log=is_log)
#p3 = ax.bar(ind + 2*width, fluxnet_mscp_avg_tput, width, yerr=fluxnet_mscp_std_tput, color='g', log=is_log)

for i, v in enumerate(als_avg_tput):
    ax.text(i, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')
    #ax.text(v + 3, i + .25, str(v), fontdict=font)

#for i, v in enumerate(fluxnet_msip_avg_tput):
for i, v in enumerate(fluxnet_msip_norm_tput):
    ax.text(i + width, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')

#for i, v in enumerate(fluxnet_mscp_avg_tput):
for i, v in enumerate(fluxnet_mscp_norm_tput):
    ax.text(i + 2*width, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')

#ax.set_xticks(ind + width / 2)
ax.set_xticks(ind + width)

ax.set_xticklabels(('Local', 'Cluster'))
ax.tick_params(labelsize=label_size)

ax.set_ylabel("Avg Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Configuration Mode", fontdict=font, labelpad=label_pad_x)

ax.legend((p1[0], p2[0], p3[0]), ('ALS-SS', 'FLUX-MSIP', 'FLUX-MSCP'), fontsize=legend_size)
#ax.set_yscale('log')

#fig.canvas.draw()
ax.relim()
ax.autoscale_view()
ax.set_ylim(top=1500)
plt.tight_layout()

graph_filename = "avg_tput_modes_1_worker_buffered_stream." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename))

plt.clf()

###########################################################################

fig, ax = plt.subplots(figsize=(figsize1,figsize2))

p1 = ax.bar(ind, als_avg_etime_latency, width, yerr=als_std_etime_latency, color='b', log=is_log)
p2 = ax.bar(ind + width, fluxnet_msip_avg_etime_latency, width, yerr=fluxnet_msip_std_etime_latency, color='r', log=is_log)
p3 = ax.bar(ind + 2*width, fluxnet_mscp_avg_etime_latency, width, yerr=fluxnet_mscp_std_etime_latency, color='g', log=is_log)

for i, v in enumerate(als_avg_etime_latency):
    ax.text(i, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')
    #ax.text(v + 3, i + .25, str(v), fontdict=font)

for i, v in enumerate(fluxnet_msip_avg_etime_latency):
    ax.text(i + width, v, "%.1f" % v, fontdict=font_bar_t,
        horizontalalignment='center', verticalalignment='bottom')

for i, v in enumerate(fluxnet_mscp_avg_etime_latency):
    if v < 1:
        ax.text(i + 2*width, v, "%.1e" % v, fontdict=font_bar_t,
            horizontalalignment='center', verticalalignment='bottom')
    else:
        ax.text(i + 2*width, v, "%.1f" % v, fontdict=font_bar_t,
            horizontalalignment='center', verticalalignment='bottom')

#ax.set_xticks(ind + width / 2)
ax.set_xticks(ind + width)

ax.set_xticklabels(('Local', 'Cluster'))
ax.tick_params(labelsize=label_size)

ax.set_ylabel("Avg Latency (s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Configuration Mode", fontdict=font, labelpad=label_pad_x)

ax.legend((p1[0], p2[0], p3[0]), ('ALS-SS', 'FLUX-MSIP', 'FLUX-MSCP'),
    fontsize=legend_size, ncol=3)
#ax.set_yscale('log')

ax.relim()
ax.autoscale_view()
ax.set_ylim(top=2500)
plt.tight_layout()

graph_filename = "et_latency_modes_1_worker_buffered_stream." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename))

plt.clf()

