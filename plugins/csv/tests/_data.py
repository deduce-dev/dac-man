"""
Utilities to expose the data to the test suite.

Might at some point include solutions to distribute the data in a more robust way,
especially w.r.t. being publicly available in plaintext.
"""

from pathlib import Path


def _contains(path, globexpr):
    # returns True if it finds at least one path matching the expression
    # this avoids loading the whole generator into memory
    # TODO review this and see if it's worth...
    for _ in Path(path).glob(globexpr):
        return True
    else:
        return False

def _is_data_directory(path):
    return _contains(path, '**/*.csv')

def _get_data_path():
    path_here = Path(__file__).resolve()
    # this assumes that this file is in the top-level tests directory
    path_tests = path_here.parent

    # this assumes that `data` is in a sibling directory wrt `tests`
    path_data = path_tests.parent / 'data'
    
    if _is_data_directory(path_data):
        return path_data
    raise ValueError(f'data directory not found or empty: {path_data}')


PATH_BASE = _get_data_path()

PATHS_BASIC = [PATH_BASE / 'test1' / name for name in ('2019DacManBasicA.csv', '2019DacManBasicB.csv')]

# TODO prepare Excel files
