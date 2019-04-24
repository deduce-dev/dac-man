import pandas as pd

from dacman_csv import TableDiffer
from dacman_csv import compare_eq, compare_numeric, compare_time

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
        'comparators': {
            'measurement_date': 'compare_time',
            'temperature': 'compare_numeric',
            'pressure': 'compare_numeric',
            'humidity': 'compare_numeric',
            'comment': 'compare_eq',
        }
    }



def test_table_differ_converts_config_values_to_objects(config):
    comparators = TableDiffer(config=config).comparators

    assert 'measurement_date' in comparators

    assert comparators['measurement_date'] == compare_time
    assert comparators['temperature'] == compare_numeric
    assert comparators['comment'] == compare_eq


@pytest.mark.parametrize('config_comparators', [
    {
        '*': 'compare_eq',
        'temperature': 'compare_numeric',
        'pressure': 'compare_numeric',
        'humidity': 'compare_numeric',
        'measurement_date': 'compare_time',
    },
    {
        '*': 'compare_numeric',
        'measurement_date': 'compare_time',
        'comment': 'compare_eq',
        'measurement_id': 'compare_eq',
    }
])
def test_column_differ_receives_correct_default(config, config_comparators):
    config['comparators'] = config_comparators
    table_differ = TableDiffer(config=config)
    comparators = table_differ.comparators

    builder = table_differ.get_builder(*PATHS)

    assert builder.get_column_differ(comparators, 'humidity').comparator == compare_numeric
    assert builder.get_column_differ(comparators, 'measurement_id').comparator == compare_eq
    assert builder.get_column_differ(comparators, 'measurement_date').comparator == compare_time