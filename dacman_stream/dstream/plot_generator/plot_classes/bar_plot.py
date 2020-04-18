import os
import numpy as np
import matplotlib.pyplot as plt
import settings as _settings
from plot_classes.plot import Plot


class BarPlot(Plot):
    def plot(self, value_arrs, xtick_labels, rotation="horizontal",
             legends=None, std_arrs=None, display_val=False, ncol=None,
             xticks_step=None, yticks_step=None):
        n_groups = len(value_arrs)
        self._n = len(value_arrs[0])
        assert n_groups <= len(self._c_list), "So far up to %d colors is supported" % len(self._c_list)

        ind = np.arange(self._n)    # the x locations for the groups

        fig, ax = plt.subplots(figsize=(self._fig_size1, self._fig_size2))

        bar_handles = []
        for i in range(n_groups):
            if std_arrs:
                p = ax.bar(ind + i*self._width, value_arrs[i], self._width,
                        yerr=std_arrs[i], color=self._c_list[i],
                        log=self._is_log_scale)
                bar_handles.append(p[0])
            else:
                p = ax.bar(ind + i*self._width, value_arrs[i], self._width,
                        color=self._c_list[i], log=self._is_log_scale)
                bar_handles.append(p[0])

            if display_val:
                for j, v in enumerate(value_arrs[i]):
                    if v < 0.1:
                        ax.text(ind[j] + i*self._width, v, "%.1e" % v, fontdict=self._inner_txt_size,
                        horizontalalignment='center', verticalalignment='bottom')
                    else:
                        ax.text(ind[j] + i*self._width, v, "%.1f" % v, fontdict=self._inner_txt_size,
                        horizontalalignment='center', verticalalignment='bottom')

        ax.set_xticks(ind + ((n_groups-1) * self._width/2))

        ax.set_xticklabels(xtick_labels, rotation=rotation)
        ax.tick_params(labelsize=self._label_size)

        if xticks_step:
            ax.set_xticks(range(0, int(ax.get_xticks()[-1]), xticks_step))

        if yticks_step:
            ax.set_yticks(range(0, int(ax.get_yticks()[-1]), yticks_step))

        ax.set_ylabel(self._ylabel, fontdict=self._font, labelpad=self._label_pad_y)
        ax.set_xlabel(self._xlabel, fontdict=self._font, labelpad=self._label_pad_x)

        if legends:
            if ncol:
                ax.legend(bar_handles, legends, ncol=ncol, loc=self._legend_loc, fontsize=self._legend_size)
            else:
                ax.legend(bar_handles, legends, ncol=n_groups, loc=self._legend_loc, fontsize=self._legend_size)

        ax.relim()
        ax.autoscale_view()
        ax.set_ylim(bottom=self._ylim_bottom, top=self._ylim_top)

        plt.tight_layout()

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        filename = self._plot_filename + "." + self._graph_ext
        plt.savefig(os.path.join(self._output_dir, filename))
