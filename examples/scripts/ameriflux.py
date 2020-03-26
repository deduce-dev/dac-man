#!/usr/bin/env python3
import sys

import dacman
from dacman.plugins.csv import CSVPlugin


class AmeriFluxPlugin(CSVPlugin):

    record_opts = {
        'table_range': {
            'row_start': 18,
        },
        'header': {
            'pos': 'rel',
            'name': 0,
            'units': 1,
            'value_ref': 2,
        },
        'dtype': True,
    }

    detail_level = 2

def run_my_change_analysis(file_a, file_b):
    comparisons = [(file_a, file_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(AmeriFluxPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    file_a, file_b = cli_args[0], cli_args[1]
    run_my_change_analysis(file_a, file_b)
