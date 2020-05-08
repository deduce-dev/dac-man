#!/usr/bin/env python3

import sys

import dacman
from dacman.plugins.json import JSONPlugin


class MyJSONPlugin(JSONPlugin):
    output_options = {'detail_level': 2}


def run_my_change_analysis(file_a, file_b):
    comparisons = [(file_a, file_b)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(MyJSONPlugin)
    differ.start()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')
    file_a, file_b = cli_args[0], cli_args[1]
    run_my_change_analysis(file_a, file_b)
