import os
import numpy as np
import matplotlib.pyplot as plt

import settings as _settings
from task_stat_generator import TaskStatGenerator


class AggregateMethod(object):
    MEAN = 0
    STD = 1
    MIN = 2
    MAX = 3
    RAW_VAL = 4
    RAW_LIST = 5


class Experiment(object):
    def __init__(self, app, data_size, experiment_path,
                 is_local=False, is_buffered=False,
                 is_pipeline=False, scaling_style=""):
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

        self.scaling_style = scaling_style

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

        def get_variable_vals(exp_results):
            variable_outputs = []
            for exp_res in exp_results:
                variable_outputs.append(exp_res[variable])
            print(variable_outputs)
            return variable_outputs

        if method == AggregateMethod.MEAN:
            for exp_results in self.results:
                agg_results.append(np.mean(get_variable_vals(exp_results)))
        elif method == AggregateMethod.STD:
            for exp_results in self.results:
                agg_results.append(np.std(get_variable_vals(exp_results)))
        elif method == AggregateMethod.MIN:
            for exp_results in self.results:
                agg_results.append(min(get_variable_vals(exp_results)))
        elif method == AggregateMethod.MAX:
            for exp_results in self.results:
                agg_results.append(max(get_variable_vals(exp_results)))
        elif method == AggregateMethod.RAW_VAL:
            for exp_results in self.results:
                agg_results.append(get_variable_vals(exp_results))
        elif method == AggregateMethod.RAW_LIST:
            for exp_results in self.results:
                variable_outputs = []
                for exp_res in exp_results:
                    variable_outputs = variable_outputs + exp_res[variable]
                agg_results.append(variable_outputs)

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
                    self.app,
                    self.mode,
                    self.data_setup,
                    self.data_size,
                    self.pipeline_setup,
                    self.scaling_style,
                    setup_n
                )
            )

        task_stat_gen = TaskStatGenerator()
        self.results = task_stat_gen.process(self._experiment_paths)
        assert len(self.results) == len(self._experiment_paths), "Results size is wrong"
