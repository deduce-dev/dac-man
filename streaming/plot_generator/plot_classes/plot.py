import os
import numpy as np
import matplotlib.pyplot as plt
import settings as _settings

class Plot(object):
    def __init__(self,
                 output_dir=_settings.PLOT_DIR, plot_filename = None,
                 xlabel="", ylabel="",
                 font_size=28, label_size=28,
                 legend_size=20, legend_loc="upper left",
                 label_pad_x=10, label_pad_y=15, inner_txt_size=16,
                 fig_size1=9, fig_size2=5,
                 graph_ext="pdf", width=0.25,
                 color_list=["blue", "red", "darkorange",
                 "olive", "saddlebrown", "purple"],
                 ylim_bottom=None, ylim_top=None, is_log_scale=False):

        self._output_dir = output_dir
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        self._n = None
        self._plot_filename = plot_filename
        self._xlabel = xlabel
        self._ylabel = ylabel

        self._font = {
            'size': font_size,
        }
        self._label_size = label_size
        self._legend_size = legend_size
        self._legend_loc = legend_loc
        self._label_pad_x = label_pad_x
        self._label_pad_y = label_pad_y
        self._inner_txt_size = {
            'size': inner_txt_size,
        }
        self._fig_size1 = fig_size1
        self._fig_size2 = fig_size2
        self._graph_ext = graph_ext

        self._width = width

        self._c_list = color_list

        self._ylim_bottom = ylim_bottom
        self._ylim_top = ylim_top
        self._is_log_scale = is_log_scale
