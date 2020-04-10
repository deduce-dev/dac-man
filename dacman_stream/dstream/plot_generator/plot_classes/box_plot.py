import matplotlib.pyplot as plt
import settings as _settings

class BoxPlot(object):
    def __init__(self, xticks_labels=None,
                 output_dir=_settings.PLOT_DIR, plot_filename = None,
                 xlabel="Number of Workers",
                 ylabel="Throughput\n(tasks/s)",
                 font_size=28, label_size=28, legend_size=20,
                 label_pad_x=10, label_pad_y=15,
                 fig_size1=9, fig_size2=5,
                 graph_ext="pdf", width=0.25, c1='b', c2='r',
                 ylim_top=None):

        self._xticks_labels = xticks_labels
        self._output_dir = output_dir

        self._n = len(self._local_val_arr)

        self._plot_filename = plot_filename
        self._xlabel = xlabel
        self._ylabel = ylabel

        self._font = {
            'size': font_size,
        }
        self._label_size = label_size
        self._legend_size = legend_size
        self._label_pad_x = label_pad_x
        self._label_pad_y = label_pad_y
        self._fig_size1 = fig_size1
        self._fig_size2 = fig_size2
        self._graph_ext = graph_ext

        self._width = width
        self._c1 = c1
        self._c2 = c2

        self._ylim_top = ylim_top
    

    def plot(self, var_arr1, var_arr2):
        ind = np.arange(self._n)    # the x locations for the groups

        fig, ax = plt.subplots(figsize=(self._fig_size1, self._fig_size2))

        p1 = ax.boxplot(var_arr1, positions=ind, patch_artist=True, widths=self._width,
                boxprops=dict(facecolor=self._c1, color=self._c1))
        p2 = ax.boxplot(var_arr2, positions=(ind+self._width), patch_artist=True, widths=self._width,
                boxprops=dict(facecolor=self._c2, color=self._c2))

        ax.set_xticks(ind + width / 2)

        if self._xticks_labels:
            ax.set_xticklabels(self._xticks_labels)
            ax.tick_params(labelsize=self._label_size)

        ax.set_ylabel(self._ylabel, fontdict=self._font, labelpad=self._label_pad_y)
        ax.set_xlabel(self._xlabel, fontdict=self._font, labelpad=self._label_pad_x)

        ax.legend((p1["boxes"][0], p2["boxes"][0]), ('Local', 'Cluster'), fontsize=self._legend_size, ncol=2, loc="upper left")

        ax.autoscale_view()

        if self._ylim_top:
            ax.set_ylim(top=self._ylim_top)

        plt.tight_layout()

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        graph_filename = self._plot_filename + "." + graph_ext
        plt.savefig(os.path.join(self._output_dir, graph_filename))
