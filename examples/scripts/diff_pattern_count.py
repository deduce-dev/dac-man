#!/usr/bin/env python3

import sys
from pathlib import Path


def get_pattern_count(filepath, pattern):

    with filepath.open('r') as f:
        try:
            count = sum([line.count(pattern) for line in f])
        except Exception as e:
            print(e)
            count = 0

    return count


def calc_difference_pattern_count(path_a, path_b, pattern):
    count_a = get_pattern_count(path_a, pattern)
    count_b = get_pattern_count(path_b, pattern)

    difference = count_a - count_b

    print(f'Analyzing changes in: how many times pattern "{pattern}" appears')
    print(f'For file "{path_a}": {count_a}')
    print(f'For file "{path_b}": {count_b}')
    print(f'Difference: {difference:+d}')


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    print(f'cli_args={cli_args}')

    path_a = Path(cli_args[0])
    path_b = Path(cli_args[1])
    pattern = 'e'

    calc_difference_pattern_count(path_a, path_b, pattern)

