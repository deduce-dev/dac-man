#!/usr/bin/env python3

import dacman
from dacman.compare import base
from dacman.compare.adaptor import DacmanRecord

import sys
import numpy
import numpy.linalg


class MatrixTxtAdaptor(base.DacmanRecordAdaptor):

    def transform(self, data_path):
        headers = []
        data = numpy.loadtxt(data_path)

        return headers, data


class MatrixTxtPlugin(base.Comparator):

    threshold = 0.01

    @staticmethod
    def description():
        return "A Dac-Man plug-in to compare matrices saved as text files"

    @staticmethod
    def supports():
        return ['txt']

    def get_record(self, path):
        ext = 'txt'

        rec = DacmanRecord(path)

        rec.file_support = {ext: True}
        rec.lib_support = {ext: 'numpy'}
        rec.file_adaptors = {ext: MatrixTxtAdaptor}

        rec._transform_source()

        return rec

    def compare(self, path_a, path_b, *args):
        rec_a = self.get_record(path_a)
        rec_b = self.get_record(path_b)

        try:
            self.metrics = self.get_matrix_change_metrics(rec_a, rec_b)
        except Exception as e:
            self.metrics = {'error': str(e)}

        return self.metrics

    def get_matrix_change_metrics(self, rec_a, rec_b):
        mat_a = rec_a.data
        mat_b = rec_b.data

        mat_delta = mat_a - mat_b

        n_values_over_threshold = numpy.sum(numpy.abs(mat_delta) > self.threshold)
        frac_changed = n_values_over_threshold / mat_delta.size

        sum_of_delta = numpy.sum(mat_delta)
        mean_of_delta = numpy.mean(mat_delta)
        norm_of_delta = numpy.linalg.norm(mat_delta)

        delta_max = numpy.max(mat_a) - numpy.max(mat_b)
        delta_min = numpy.min(mat_a) - numpy.min(mat_b)

        return {
            'frac_changed': frac_changed,
            'sum(A - B)': sum_of_delta,
            'mean(A - B)': mean_of_delta,
            'norm(A - B)': norm_of_delta,
            'delta(max(A) - max(B))': delta_max,
            'delta(min(A) - min(B))': delta_min,
        }

    def percent_change(self):
        frac = self.metrics.get('frac_changed', 0)
        return frac * 100

    def stats(self, changes):
        print(changes)


def run_matrix_change_ana(path_a, path_b):
    comparisons = [(path_a, path_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(MatrixTxtPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    path_a, path_b = cli_args[0], cli_args[1]
    run_matrix_change_ana(path_a, path_b)
