import pandas as pd
from dacman_csv import TableDiffer

import pytest

from ._data import PATHS_2 as PATHS


def process_test2(df):
    return (df
            .assign(measurement_date=lambda d: pd.to_datetime(d['measurement_date']))
           )


@pytest.fixture
def config():
    return {
        'load_mode': 'csv',
        'rename_fields': {
            'date': 'measurement_date',
        },
        'process_func': process_test2,
        'index_fields': 'measurement_id',
        'sort_fields': 'measurement_id',
    }


@pytest.fixture
def config_with_no_process(config):
    config.pop('process_func')
    return config


def test_differ_from_config_works(config):
    differ = TableDiffer(config=config)

    builder = differ.get_builder(*PATHS)


# TODO this OBVIOUSLY should be a parametrized fixture
def test_differ_works_with_config_with_no_set_process(config_with_no_process):
    differ = TableDiffer(config=config_with_no_process)

    builder = differ.get_builder(*PATHS)


def test_config_from_file_is_equivalent(config):
    path = PATHS[0].parent / 'config.py'

    # TODO this obviously relies on the fact that these two are actually the same
    differ_1 = TableDiffer(config=config)
    differ_2 = TableDiffer.from_config_py(path)

    # this will fail because the functions are different objects
    # assert differ_1.config == differ_2.config

    pd.testing.assert_frame_equal(
        differ_1.get_builder(*PATHS).data[0],
        differ_2.get_builder(*PATHS).data[0],
    )