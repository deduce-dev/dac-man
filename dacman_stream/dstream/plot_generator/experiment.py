import os
import numpy as np
import matplotlib.pyplot as plt

import settings as _settings
from stat_generator import StatGenerator

class AggregateMethod(object):
    MEAN = 0
    STD = 1
    MIN = 2
    MAX = 3


class Experiment(object):
    def __init__(self, app, data_size, experiment_path,
                 is_local=False, is_buffered=False, is_pipeline=False):
        self.app = app
        self.data_size = data_size
        self.experiment_path = experiment_path

        if is_local:
            self.mode = "local"
        else:
            self.mode = "cori"

        if is_buffered:
            self.data_setup = "pre_stream"
        else:
            self.data_setup = "live_stream"

        if is_pipeline:
            self.pipeline_setup = "pipeline"
        else:
            self.pipeline_setup = "non_pipeline"

        self._setups = []
        self._experiment_paths = []

        self.results = []

    def add_setup(self, n_sources, n_workers):
        '''
        Add a setup in the format s_2_w_1 for example
        '''
        self._setups.append("s_%d_w_%d" % (n_sources, n_workers))

    def set_results(self, results):
        self.results = results

    def get_agg_results(self, variable, method=AggregateMethod.MEAN):
        '''
        Get aggregated results -- so far avg/mean is implemented
        '''
        agg_results = []

        if method == AggregateMethod.MEAN:
            for res in self.results:
                agg_results.append(np.mean(res[variable]))
        elif method == AggregateMethod.STD:
            for res in self.results:
                agg_results.append(np.std(res[variable]))
        elif method == AggregateMethod.MIN:
            for res in self.results:
                agg_results.append(min(res[variable]))
        elif method == AggregateMethod.MAX:
            for res in self.results:
                agg_results.append(max(res[variable]))

        return agg_results

    def process(self):
        '''
        Get results for the specified setups
        '''
        # create experiment full path
        for setup_n in self._setups:
            self._experiment_paths.append(
                os.path.join(
                    self.experiment_path,
                    self.mode,
                    self.self.data_setup,
                    self.data_size,
                    self.pipeline_setup,
                    setup_n
                )
            )

        stat_gen = StatGenerator()
        self.results = stat_gen.process(self._experiment_paths)

