import matplotlib.pyplot as plt
import settings as _settings

class BarPlot(object):
    def __init__(self,
                 output_dir=_settings.PLOT_DIR, plot_filename = None,
                 xlabel="",
                 ylabel="",
                 font_size=28, label_size=28, legend_size=20,
                 label_pad_x=10, label_pad_y=15,
                 fig_size1=9, fig_size2=5,
                 graph_ext="pdf", width=0.25, c1='b', c2='r',
                 is_log_scale=False):
    
        self._output_dir = output_dir

        self._n = None
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
        self._c_list = [
            "royalblue",
            "red",
            "darkorange",
            "olive"
        ]

        self._is_log_scale = is_log_scale
    

    def plot(self, value_arrs, bar_labels, xtick_labels, std_arrs=None):
        n_bars = len(value_arrs)
        self._n = len(value_arrs[0])
        assert n_bars <= 4, "So far up to 4 bars is supported"

        ind = np.arange(self._n)    # the x locations for the groups

        fig, ax = plt.subplots(figsize=(self._fig_size1, self._fig_size2))

        ax_bars = []
        if std_arrs:
            for i in range(n_bars):
                ax_bars.append(
                    ax.bar(ind + i*self._width, value_arrs[i], width,
                        yerr=std_arrs[i], color=self._c_list[i],
                        log=self._is_log_scale)
                )
        else:
            for i in range(n_bars):
                ax_bars.append(
                    ax.bar(ind + i*self._width, value_arrs[i], width,
                        color=self._c_list[i], label=bar_labels[i],
                        log=self._is_log_scale)
                )

        ax.set_xticks(ind + ((n_bars-1) * width/2))

        ax.set_xticklabels(xtick_labels)
        ax.tick_params(labelsize=self._label_size)

        ax.set_ylabel(self._ylabel, fontdict=self._font, labelpad=self._label_pad_y)
        ax.set_xlabel(self._xlabel, fontdict=self._font, labelpad=self._label_pad_x)

        ax.legend(ncol=n_bars, loc="upper left")

        #ax.ylim(bottom=0)

        plt.tight_layout()

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        graph_filename = self._plot_filename + "." + graph_ext
        plt.savefig(os.path.join(self._output_dir, graph_filename))
