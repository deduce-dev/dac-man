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
    'comparators':     {
        '*': 'compare_numeric',
        'measurement_date': 'compare_time',
        'site_id': 'compare_eq',
        'comment': 'compare_eq',
        'measurement_id': 'compare_eq',
    }
}
