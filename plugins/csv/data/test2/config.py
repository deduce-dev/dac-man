import pandas as pd


def process_test2(df):
    return (df
            .assign(measurement_date=lambda d: pd.to_datetime(d['measurement_date']))
           )

CONFIG = {
    'load_mode': 'csv',
    'rename_fields': {
        'date': 'measurement_date',
    },
    'process_func': process_test2,
    'index_fields': 'measurement_id',
    'sort_fields': 'measurement_id',
}
