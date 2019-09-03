#!/usr/bin/env python3
import sys

import dacman
from dacman.plugins.csv import CSVPlugin


class MyCSVPlugin(CSVPlugin):

    calc_options = {
        'header_pos': 0,
        'index': 'site_id',
        'column_renames': {'day': 'date'},
        'dtype': True
    }


def run_my_change_analysis(file_a, file_b):
    comparisons = [(file_a, file_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(MyCSVPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    file_a, file_b = cli_args[0], cli_args[1]
    run_my_change_analysis(file_a, file_b)

