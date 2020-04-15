import os
import numpy as np
import matplotlib.pyplot as plt
import settings as _settings
from plot_classes.plot import Plot


class LinePlot(Plot):
    def plot(self, value_arrs, xtick_labels, fmt, legends=None):
        n_groups = len(value_arrs)
        self._n = len(value_arrs[0])
        assert n_groups <= 4, "So far up to 4 bars is supported"

        ind = np.arange(self._n)    # the x locations for the groups

        fig, ax = plt.subplots(figsize=(self._fig_size1, self._fig_size2))

        line_handles = []
        for i in range(n_groups):
            if fmt:
                p = ax.plot(ind, value_arrs[i], fmt, color=self._c_list[i])
                line_handles.append(p[0])
            else:
                p = ax.plot(ind, value_arrs[i], color=self._c_list[i])
                line_handles.append(p[0])

        ax.set_xticks(ind + ((n_groups-1) * self._width/2))

        ax.set_xticklabels(xtick_labels)
        ax.tick_params(labelsize=self._label_size)

        ax.set_ylabel(self._ylabel, fontdict=self._font, labelpad=self._label_pad_y)
        ax.set_xlabel(self._xlabel, fontdict=self._font, labelpad=self._label_pad_x)

        if self._is_log_scale:
            ax.set_yscale('log')

        ax.set_ylim(bottom=self._ylim_bottom, top=self._ylim_top)

        if legends:
            ax.legend(line_handles, legends, ncol=n_groups, loc=self._legend_loc, fontsize=self._inner_txt_size)

        plt.tight_layout()

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        filename = self._plot_filename + "." + self._graph_ext
        plt.savefig(os.path.join(self._output_dir, filename))
