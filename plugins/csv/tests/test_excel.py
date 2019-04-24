import pandas as pd
from dacman_csv import TableDiffer

import pytest

from ._data import PATHS_3 as PATHS


# def process_test2(df):
#     return (df
#             .assign(measurement_date=lambda d: pd.to_datetime(d['measurement_date']))
#            )


@pytest.fixture
def config():
    return {
        'load_mode': 'excel',
        'load_opts': {
            'usecols': 'C:I',
            'skiprows': list(range(14)),
            'header': 0,
            'nrows': 21,
        },
        'rename_fields': {
            'date': 'measurement_date',
        },
        # 'process_func': process_test2,
        'index_fields': 'measurement_id',
        'sort_fields': 'measurement_id',
    }


def test_differ_from_config_works(config):
    differ = TableDiffer(config=config)

    builder = differ.get_builder(*PATHS)
