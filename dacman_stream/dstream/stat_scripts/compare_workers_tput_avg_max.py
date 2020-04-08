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

output_dir = sys.argv[1]
is_log = False

###################################################################################
############################# Buffered Stream #####################################
###################################################################################

# ALS
als_avg_tput = [5.597014925373134, 5.639097744360902, 6.147540983606557, 6.185567010309279, 6.342494714587738]
als_std_tput = [2.6720482472437, 2.795910939734534, 3.9808396246486497, 4.392894677495862, 4.317356645728989]
als_max_tput = [20, 35, 47, 60, 50]

N = 5

ind = np.arange(N)    # the x locations for the groups
width = 0.25         # the width of the bars
bar_label_diff = 0.1

fig, ax = plt.subplots(figsize=(figsize1,figsize2))

p1 = ax.bar(ind, als_avg_tput, width, yerr=als_std_tput, color='b', log=is_log)
#p2 = ax.bar(ind + width, als_max_tput, width, color='r', log=is_log)

#ax.set_xticks(ind + width / 2)
ax.set_xticks(ind)

ax.set_xticklabels(('64', '128', '256', '512', '640'))
ax.tick_params(labelsize=label_size)

ax.set_ylabel("Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Number of Workers", fontdict=font, labelpad=label_pad_x)

#ax.legend((p1[0], p2[0]), ('Avg', 'Max'), fontsize=legend_size, ncol=2)
#ax.set_yscale('log')

#fig.canvas.draw()
ax.relim()
ax.autoscale_view()
ax.set_ylim(top=12)
plt.tight_layout()

graph_filename = "als_tput_buffered_stream_avg_max." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename))

plt.clf()

###########################################################################

# Scenario A
#fluxnet_msip_avg_tput = [4574.521739130435, 8093.384615384615, 11690.444444444445, 13151.75, 17535.666666666668]
#fluxnet_msip_std_tput = [1478.132954823789, 3444.3506151034208, 3871.1353233073655, 4833.9229345842905, 5691.139038501481]
#fluxnet_msip_max_tput = [5914, 11665, 15014, 15747, 21682]

#fluxnet_msip_avg_tput = [4574.521739130435, 8093.384615384615, 10521.4, 13151.75, 15030.57142857143]
#fluxnet_msip_std_tput = [1478.132954823789, 3444.3506151034208, 5090.579086901607, 4690.4250007328765, 2901.1367159956385]
#fluxnet_msip_max_tput = [5914, 11665, 15688, 16124, 20062]

fluxnet_msip_avg_tput = [4782.454545454545, 5537.578947368421, 13151.75, 13151.75, 13151.75]
fluxnet_msip_std_tput = [1480.9613194651865, 4369.872120443626, 3135.4185426350978, 5914.182313515538, 4972.096080879774]
fluxnet_msip_max_tput = [5786, 11675, 15536, 17641, 15977]


N = 5

ind = np.arange(N)    # the x locations for the groups
width = 0.25         # the width of the bars
bar_label_diff = 0.1

fig, ax = plt.subplots(figsize=(figsize1,figsize2))

p1 = ax.bar(ind, fluxnet_msip_avg_tput, width, yerr=fluxnet_msip_std_tput, color='b', log=is_log)
#p2 = ax.bar(ind + width, fluxnet_msip_max_tput, width, color='r', log=is_log)

#ax.set_xticks(ind + width / 2)
ax.set_xticks(ind)

ax.set_xticklabels(('64', '128', '256', '512', '640'))
ax.tick_params(labelsize=label_size)

ax.set_ylabel("Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Number of Workers", fontdict=font, labelpad=label_pad_x)

#ax.legend((p1[0], p2[0]), ('Avg', 'Max'), fontsize=legend_size, ncol=2)
#ax.set_yscale('log')

#fig.canvas.draw()
ax.relim()
ax.autoscale_view()
ax.set_ylim(top=20000)
plt.tight_layout()

graph_filename = "flux_msip_tput_buffered_stream_avg_max." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename))

plt.clf()

###########################################################################

# Scenario B
#fluxnet_mscp_avg_tput = [3757.714285714286, 7515.428571428572, 10521.6, 10521.6, 10521.6]
#fluxnet_mscp_std_tput = [2094.786331707892, 2322.9949177204635, 4059.3405178674034, 6264.852004636662, 4977.063214386572]
#fluxnet_mscp_max_tput = [5909, 11362, 13885, 15824, 16052]

fluxnet_mscp_avg_tput = [3288.0, 5845.333333333333, 10521.6, 13152.0, 13152.0]
fluxnet_mscp_std_tput = [1491.7264745924435, 4120.618346262555, 4059.3405178674034, 3031.139967075094, 2880.2492079679496]
fluxnet_mscp_max_tput = [5470, 11710, 13885, 15706, 15976]
N = 5

ind = np.arange(N)    # the x locations for the groups
width = 0.25         # the width of the bars
bar_label_diff = 0.1

fig, ax = plt.subplots(figsize=(figsize1,figsize2))

p1 = ax.bar(ind, fluxnet_mscp_avg_tput, width, yerr=fluxnet_mscp_std_tput, color='b', log=is_log)
#p2 = ax.bar(ind + width, fluxnet_mscp_max_tput, width, color='r', log=is_log)

#ax.set_xticks(ind + width / 2)
ax.set_xticks(ind)

ax.set_xticklabels(('64', '128', '256', '512', '640'))
ax.tick_params(labelsize=label_size)

ax.set_ylabel("Throughput\n(tasks/s)", fontdict=font, labelpad=label_pad_y)
ax.set_xlabel("Number of Workers", fontdict=font, labelpad=label_pad_x)

#ax.legend((p1[0], p2[0]), ('Avg', 'Max'), fontsize=legend_size, ncol=2)
#ax.set_yscale('log')

#fig.canvas.draw()
ax.relim()
ax.autoscale_view()
ax.set_ylim(top=20000)
plt.tight_layout()

graph_filename = "flux_mscp_tput_buffered_stream_avg_max." + graph_ext
plt.savefig(os.path.join(output_dir, graph_filename))

plt.clf()

