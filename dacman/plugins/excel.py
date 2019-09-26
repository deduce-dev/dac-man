from pathlib import Path
import numpy as np

try:
    import pandas as pd
except ImportError:
    from dacman.core.utils import dispatch_import_error
    dispatch_import_error(module_name='pandas', plugin_name='Excel')

try:
    import xlrd
except ImportError:
    from dacman.core.utils import dispatch_import_error
    dispatch_import_error(module_name='xlrd', plugin_name='Excel')

from .csv import (
    ChangeStatus as _S,
    _InternalFields as _F
    )

from . import csv


class WorksheetTableColumnsRecord(csv.CSVTableColumnsRecord):

    @staticmethod
    def to_excel_colnames(df):
        return df.rename(columns=xlrd.formula.colname)

    def __init__(self, *args, worksheet_id=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.worksheet_id = worksheet_id

    def get_worksheet_frame(self, index_col=_F.LOC_ORIG_ROW):
        load_opts = dict(dtype=object, header=None, sheet_name=self.worksheet_id)
        df = pd.read_excel(self.src, **load_opts)

        return (df
                .pipe(self.to_excel_colnames)
                .assign(**{_F.LOC_ORIG_ROW: df.index + 1})
                .set_index(index_col, drop=True)
               )

    def get_worksheet_subset(self, df,
                             row_start=1, row_end=None, n_rows=None,
                             col_start='A', col_end=None, n_cols=None
                            ):

        # display(df)

        if row_end is None and n_rows is not None:
            row_end = row_start + n_rows

        if col_end is None and n_cols is not None:
            row_end = row_start + n_cols

        return df.loc[row_start:row_end, col_start:col_end]

    def get_table_orig(self):
        return (self.get_worksheet_frame()
                .pipe(self.get_worksheet_subset, **self.table_range)
               )


class ExcelPlugin(csv.CSVPlugin):
    "Analyze changes in Excel spreadsheets interpreted as tabular data."

    @staticmethod
    def supports():
        # TODO check if there are other file extensions that are compatible with this implementation
        return ['xls', 'xlsx', 'xlsm']

    def get_record_columns(self, *args, **kwargs):
        """
        Return the Record object used to fetch, process and expose for comparison table columns.
        """
        rec = WorksheetTableColumnsRecord(*args, **self.record_opts, **kwargs)
        rec.load()

        return rec

    def get_file_metadata(self, src):
        md = {}

        path = Path(src)
        md['path_parent'] = path.parent
        md['filename'] = path.name

        book = xlrd.open_workbook(src)
        md['sheet_names'] = book.sheet_names()

        return md
