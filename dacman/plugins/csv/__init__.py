from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd

from dacman.compare import base

try:
    from IPython.display import display  # for debugging
except ImportError:
    display = print


class ChangeStatus:
    added = 'ADDED'
    deleted = 'DELETED'
    modified = 'MODIFIED'
    unchanged = 'UNCHANGED'
    unset = 'UNSET'

    @classmethod
    def iter(cls):
        yield from (cls.added, cls.deleted, cls.modified, cls.unchanged)
_S = ChangeStatus


class _InternalFields:
    """
    Utility class to access commonly used table/dict fields as constants rather than bare strings.
    """
    LINENO = '__lineno'
    ROWIDX = '__rowidx'

    ORIG = 'orig'
    CALC = 'calc'
_F = _InternalFields


class ChangeMetricsBase:
    """
    Convenience class to access properties from items being compared and calculate comparison metrics from them.
    """
    def __init__(self, key, a=None, b=None):
        self.key = key
        self.a = a
        self.b = b

        self._comparison_data = {
            'status': _S.unset,
            'metadata': {
                'common': {},
                'changes': {},
            },
        }
        
    def __setitem__(self, key, val):
        self._comparison_data[key] = val
        
    def __getitem__(self, key):
        return self._comparison_data[key]

    def keys(self):
        # TODO maybe enforce some order?
        return self._comparison_data.keys()
    
    def add(self, other_data):
        self._comparison_data.update(other_data)

    @property
    def properties(self):
        # only interested in common fields, since we have to compare them directly
        # return self.a.keys() & self.b.keys()
        # use a dict with dummy values as an ordered set to preserve the order
        dict_for_ordered_set = {key: None for key in self.a.keys() if key in self.b.keys()}
        return dict_for_ordered_set.keys()

    @property
    def is_missing_a(self):
        return len(self.a) == 0

    @property
    def is_missing_b(self):
        return len(self.b) == 0

    def change_in(self, prop):
        if prop not in self.properties:
            return False
        try:
            return self.a[prop] != self.b[prop]
        except Exception as e:
            print(e)
            return False

    def get_value_common(self, prop):
        if prop in self.properties and not self.change_in(prop):
            return self.a[prop]
        # maybe use a sentinel value other than None here?
        return None

    def get_value_single(self, prop):
        if self.is_missing_a:
            return self.b[prop]
        if self.is_missing_b:
            return self.a[prop]
        return self.get_value_common(prop)

    def get_values(self, prop, orient=dict, convert=None, as_type=None, fallback=None):
        if convert is None and as_type is not None:
            convert = as_type

        convert = convert or (lambda x: x)

        val_a = convert(self.a.get(prop, fallback))
        val_b = convert(self.b.get(prop, fallback))

        if orient in {tuple, list}:
            return val_a, val_b

        if orient in {dict}:
            return {'a': val_a, 'b': val_b}

    @property
    def is_modified(self):
        # TODO change if we use multiple modified states
        return self['status'] in {_S.modified}

    @is_modified.setter
    def is_modified(self, val):
        if bool(val) is True:
            # TODO manage other types as extra "modified" characterizers
            # e.g. if `val` is a list, append to self['modified_labels']
            self['status'] = _S.modified

    def store_common_value_or_values(self, prop):
        # TODO there could be some redundant logic in general in this class

        if self.change_in(prop):
            self['metadata']['changes'][prop] = self.get_values(prop, orient=dict)
            self.is_modified = True
        else:
            self['metadata']['common'][prop] = self.get_value_single(prop)

    def calculate(self, exclude=None):
        exclude = exclude or set()

        if self.is_missing_a:
            self['status'] = _S.added
        elif self.is_missing_b:
            self['status'] = _S.deleted

        for prop in self.properties:
            if prop not in exclude:
                self.store_common_value_or_values(prop)
        
        if self['status'] == _S.unset:
            self['status'] = _S.unchanged


class TableColumnChangeMetrics(ChangeMetricsBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._supports_numeric_delta = None

    @property
    def supports_numeric_delta(self):
        return self._supports_numeric_delta

    def calculate(self):

        super().calculate(exclude='values_frame')

        if self['status'] == _S.unset:
            self['status'] = _S.unchanged

    def calculate_from_value_metrics(self, value_metrics_table):
        col_metrics_from_value_metrics = self.get_column_metrics_from_values(value_metrics_table)

        if col_metrics_from_value_metrics['frac_changed'] > 0.:
            self.is_modified = True

        self['values'] = col_metrics_from_value_metrics

    def get_column_metrics_from_values(self, metrics_table: pd.DataFrame):
        m = {}
        df = metrics_table

        n_total = len(df)

        m['n_unchanged'] = (df['status'] == _S.unchanged).sum()
        m['n_added'] = (df['status'] == _S.added).sum()
        m['n_deleted'] = (df['status'] == _S.deleted).sum()
        m['n_modified'] = (df['status'] == _S.modified).sum()
        m['n_changed'] = (m['n_added'] + m['n_deleted'] + m['n_modified'])

        m['frac_changed'] = m['n_changed'] / n_total

        if self.supports_numeric_delta:
            m['delta_mean'] = df['delta'].mean()
            m['delta_std'] = df['delta'].std()

        return m

    def get_stats(self):
        stats = {'name': self.key}
        stats.update(self['values'])
        stats['status'] = self['status']

        return stats


class _BaseRecord:

    @staticmethod
    def default_key_getter(item):
        raise NotImplementedError

    def __init__(self, key_getter=None, **kwargs):
        super().__init__(**kwargs)

        self.key_getter = key_getter or type(self).default_key_getter

        self._mapping = self.get_mapping()

    def get_mapping(self):
        return {}

    def keys(self):
        return self._mapping.keys()

    def __getitem__(self, key):
        return self._mapping[key]

    def get_empty(self):
        return dict()

    def get(self, key):
        # TODO should we customize the default return type at the level of the class or of the instance?
        return self._mapping.get(key, self.get_empty())


class TableColumnsRecord(_BaseRecord):

    # TODO this class should probably also deal with the field renames,
    # i.e. should receive a mapping with the field renames 
    def __init__(self, loader, **kwargs):
        self.loader = loader
        super().__init__(**kwargs)

    @property
    def dataframe(self):
        return self.loader.to_table_dtype()

    def get_metadata(self, series, name):
        md = {}

        md['name'] = name
        md['series'] = series

        md['dtype'] = series.dtype

        md['n_notnull'] = series.notnull().sum()
        md['n_null'] = series.isna().sum()

        return md

    def default_key_getter(self, col_metadata):
        return col_metadata['name']

    def get_mapping(self):
        df = self.dataframe

        mapping = {}

        for colname in df:

            # TODO in general the metadata collecting can also be done directly in the Record,
            # since here we don't have several types of items at the same level like in the HDF5 plug-in
            col_md = self.get_metadata(series=df[colname], name=colname)
            # we don't need a specific record for table fields, since these are collected as metadata of the columns

            mapping[self.key_getter(col_md)] = col_md

        return mapping


def get_lines_frame(path, comment_char=None) -> pd.DataFrame:
    """Read lines and associated metadata from a file"""
    with Path(path).open() as f:
        lines = pd.DataFrame({'content': list(f)})
        lines['lineno'] = lines.index + 1

    def is_comment(s):
        if comment_char is None:
            # get a series where all values are False
            return s == np.nan
        return (s
                .astype(str)
                .str.startswith(comment_char)
                )

    lines['is_comment'] = is_comment(lines['content'])

    return lines


# TODO move to util module
def convert_dtypes(df, converters=None):
    converters = converters or [pd.to_datetime, pd.to_numeric]

    for colname in df:
        col = df[colname]

        if col.dtype == 'object':

            for conv in converters:
                try:
                    col = conv(col)
                except (TypeError, ValueError):
                    pass
                else:
                    df.loc[:, colname] = col
                    break

    return df


class CSVTableColumnsRecord(_BaseRecord):

    def __init__(self, src,
                 comment_char=None,
                 skip_lines=None,
                 header_pos=None,
                 process_func=None,
                 column_renames=None, index='rowidx', dtype=None):
        self.src = src

        self.comment_char = comment_char

        self.skip_lines = skip_lines
        self.header_pos = header_pos

        self.process_func = process_func

        self.column_renames = column_renames or {}
        self.index = index
        self.dtype = dtype

        self._colnames_stages = {}

        # super().__init__()
        self._mapping = {}

    def get_lineno_uncommented(self):
        """
        Return a sequence containing the line numbers (1-based) of uncommented lines in the source.

        This is used to associate table index/rows with their position in the source.
        """

        lines = get_lines_frame(self.src, comment_char=self.comment_char)

        return lines[~lines['is_comment']]['lineno'].to_list()

    def store_colnames(self, cols, stage_key):
        """
        Save colnames at a particular stage of table processing.
        """
        self._colnames_stages[stage_key] = list(cols)

    @property
    def colnames_frame(self):
        """
        Return colnames stages as a dataframe for more convenient indexing.
        """
        return pd.DataFrame(self._colnames_stages)

    def get_colname(self, colname, stage_from, stage_to):
        return self.colnames_frame.set_index(stage_from)[stage_to][colname]

    def _is_internal(self, colname):
        """
        Check whether a colname is one of the internal fields.
        """
        return colname in {_F.LINENO, _F.ROWIDX}

    def get_colnames_from_row(self, row):
        """
        Return valid colnames from a table row, filtering out internal fields and invalid values.
        """
        colnames = []
        for current_name, name_from_row in row.items():
            # TODO are there cases where we want to use non-string colnames?
            if isinstance(name_from_row, str) and not self._is_internal(name_from_row):
                colname = name_from_row
            else:
                colname = current_name
            colnames.append(colname)
        
        return colnames

    def get_table_orig(self):
        """
        Return the contents of the CSV file as a dataframe in the `orig` format.

        All valid (uncommented) lines are loaded as dataframe rows,
        with all values treated as text and without any processing applied.
        """
        df = pd.read_csv(self.src, dtype=str, header=None, comment=self.comment_char)
        df[_F.LINENO] = self.get_lineno_uncommented()
        df[_F.ROWIDX] = df.index

        df.columns.name = 'colidx'
        # from now on we assume that orig has lineno as index, so don't edit here!
        df = df.set_index(_F.LINENO, drop=False)

        # filling NaNs with whitespacee should only be done when displaying,
        # since otherwise it would make it harder or impossible to convert to numeric dtypes
        # df = df.fillna('')

        return df

    def get_table_calc(self, table_orig):
        """
        Return the contents of the CSV file in the `calc` format,
        i.e. the format that will be used in the change calculations.

        All processing is applied here according to the Record's options.
        """
        # The operations done here are very similar to calling read_csv() on the `orig` frame,
        # and an alternative strategy would be to convert `orig` to an in-memory string,
        # and loading it to a typed data table with read_csv().
        # But the information about the lineno in the original file would be lost.

        df = table_orig.copy()

        if self.skip_lines:
            df = df[df[_F.ROWIDX].isin(self.skip_lines)]

        self.store_colnames(df.columns, 'colidx')

        if self.header_pos is not None:
            header_row = df.iloc[self.header_pos]
            colnames_from_header = self.get_colnames_from_row(header_row)

            df.columns = colnames_from_header

            df = df[df[_F.ROWIDX] != self.header_pos]

        self.store_colnames(df.columns, 'name_header')

        if self.column_renames:
            df = df.rename(columns=self.column_renames)

        self.store_colnames(df.columns, 'name')

        # TODO also give self.src in input to do source-specific processing?
        if self.process_func:
            df = self.process_func(df)

        index_col = None

        if self.index == 'lineno':
            # because we assume that orig is always indexed with lineno?
            # but things could change in e.g. process_func
            pass
            # index_col = _F.LINENO
            # df = df.set_index(index_col, drop=False)

        # this should be the default
        elif self.index == 'rowidx':
            index_col = _F.ROWIDX
            df = df.reset_index(drop=True).set_index(index_col, drop=False)
        elif self.index is not None:
            # if self.index is not one of the internal fields, drop it since it would give redundant results anyway
            df = df.reset_index(drop=True).set_index(self.index, drop=True).sort_index()
        else:
            # maybe here we should raise a ValueError/KeyError instead?
            df = df.reset_index(drop=True)

        if self.dtype is True:
            # df = df.infer_objects()
            df = df.pipe(convert_dtypes)

        return df

    def load(self):
        self._table_orig = self.get_table_orig()
        self._table_calc = self.get_table_calc(self._table_orig)

        self._mapping = self.get_mapping()

    @property
    def table_orig(self):
        return self._table_orig

    @property
    def table_calc(self):
        return self._table_calc

    def get_colvalues_frame(self, colname):
        """
        Return a dataframe containing values for a table data column (after processing)
        associated with the corresponding grid values (raw, i.e. before processing)
        """
        join_colname = _F.LINENO

        # rename before merging, in case colname and colidx are the same
        # otherwise both will be mangled when merging
        col_calc = (self.table_calc[[colname, join_colname]]
                    .rename(columns={colname: _F.CALC})
                   )

        colidx = self.get_colname(colname, 'name', 'colidx')
        # TODO maybe we can also merge directly on a series, if it has the same index?
        col_orig = (self.table_orig[[colidx]]
                    .rename(columns={colidx: _F.ORIG})
                   )

        # this seems to be necessary if we always want to have a __lineno column,
        # regardless of whether it's also the index or not,
        # since when it's both colname and indexname df.merge() will complain of ambiguity
        opts = dict(right_index=True)
        if col_calc.index.name == join_colname:
            opts['left_index'] = True
        else:
            opts['left_on'] = join_colname

        merged = col_calc.merge(col_orig, **opts)

        return (merged
                [[_F.ORIG, _F.CALC, join_colname]]
               )

    def key_getter(self, col_metadata):
        return col_metadata['name']

    def get_metadata(self, colname):
        md = {}

        md['name'] = colname
        md['name_header'] = self.get_colname(colname, 'name', 'name_header')
        md['colidx'] = self.get_colname(colname, 'name', 'colidx')

        colvalues = self.get_colvalues_frame(colname)

        md['dtype'] = colvalues['calc'].dtype

        md['values_frame'] = colvalues

        return md

    def get_mapping(self):

        mapping = {}

        for colname in [c for c in self.table_calc if not self._is_internal(c)]:
            col_md = self.get_metadata(colname)

            mapping[self.key_getter(col_md)] = col_md

        return mapping

    def get_empty(self):
        return {'values_frame': pd.DataFrame([], columns=[_F.ORIG, _F.CALC, _F.LINENO])}


class TableValuesRecord(_BaseRecord):

    def __init__(self, src: pd.DataFrame, **kwargs):
        self.src = src
        super().__init__(**kwargs)

    def get_mapping(self):
        df = self.src

        mapping = {}

        for colname in df:
            col = df[colname]
            for row_idx in col.index:
                # this is basically the anti-pandas, but this is just here as an example
                key = (colname, row_idx)
                val = col[row_idx]

                mapping[key] = val

        return mapping


class TableColumnValuesChangeMetrics:
    """
    Calculate change metrics on a per-value basis using indexed containers.

    Instead of calculating value-level changes as a separate step,
    i.e. creating a Record from each values frame and looping over matching pairs,
    we use the fact that the value frame's index allow vectorized operations with similar semantics.
    """

    @classmethod
    def from_column_metrics(cls, col_metrics):
        values_a, values_b = col_metrics.get_values('values_frame', orient=tuple)
        
        return cls(values_a, values_b, col_metrics=col_metrics)


    def __init__(self, values_a, values_b, col_metrics=None):
        self.values_a = values_a
        self.values_b = values_b
        self.col_metrics = col_metrics

        self._table = None

    def get_table(self):

        def rename_values_frame(df, key):
            map_names = {
                _F.CALC: f'{key}_calc',
                _F.ORIG: f'{key}_orig',
                _F.LINENO: f'{key}_lineno'
            }

            return df.rename(columns=map_names)

        a = self.values_a.pipe(rename_values_frame, 'a')
        b = self.values_b.pipe(rename_values_frame, 'b')

        # outer join: union of the two column's indices
        df = (pd.concat([a, b], axis='columns', join='outer', sort=True)
              # convert again lineno to int dtype after NaNs have been introduced with the outer join
              .astype({'a_lineno': 'Int64', 'b_lineno': 'Int64'})
             )
        
        return df

    @property
    def table(self):
        return self._table

    def calculate(self):

        self._table = (self.get_table()
                       .pipe(self.calc_change_metrics_base)
                       .pipe(self.calc_delta)
                       .pipe(self.assign_change_status)
                      )

        return self.get_per_status_metrics()

    def calc_change_metrics_base(self, df):

        df.loc[:, 'is_equal'] = df['a_calc'] == df['b_calc']
        df.loc[:, 'is_null_a'] = df['a_calc'].isna()
        df.loc[:, 'is_null_b'] = df['b_calc'].isna()
        df.loc[:, 'is_null_both'] = df['is_null_a'] & df['is_null_b']
        df.loc[:, 'is_null_any'] = df['is_null_a'] | df['is_null_b']

        return df

    def calc_delta(self, df):
        # here one could add more specific deltas, e.g. depending on dtype or column name (which is self.key)

        # check if datatype is numeric, or try with exceptions?
        # functions to check are: pandas.api.types.is_number etc
        # TODO since we need to know whether we can do numeric calculations or not in several places,
        # we could store this information as an attribute/property
        try:
            # strictly speaking, this is not the delta, since delta is usually b - a
            # so we might consider changing the name
            delta = df['a_calc'] - df['b_calc']
        except TypeError:
            self._supports_numeric_delta = False
            delta = np.nan
        else:
            self._supports_numeric_delta = True

        df.loc[:, 'delta'] = delta

        return df

    def is_value_modified(self, df):
        # TODO if we factor this out, it can be customized separately
        return ~df['is_equal']

    def assign_change_status(self, df):
        # TODO additional logic here would be e.g. implementing per-field or per-dtype thresholds
        # TODO make this a categorical
        status = pd.Series(_S.unset, index=df.index)

        status[df['is_null_a'] & (~df['is_null_b'])] = _S.added
        status[(~df['is_null_a']) & df['is_null_b']] = _S.deleted

        status[(~df['is_equal']) & (~df['is_null_any'])] = _S.modified
        status[status == _S.unset] = _S.unchanged

        df.loc[:, 'status'] = status

        return df

    def get_per_status_metrics(self):
        m = {}

        for status in [_S.unchanged, _S.added, _S.deleted, _S.modified]:
            m_status = {}
            values_with_status = self._table[lambda d: d['status'] == status]

            f_aggregated = self.map_status_function_aggregated[status]
            m_status.update(f_aggregated(values_with_status))

            f_per_value = self.map_status_function_per_value[status]

            if f_per_value is not None:
                if len(values_with_status) > 0:
                    per_value_metrics = values_with_status.apply(f_per_value, axis=1).to_list()
                else:
                    per_value_metrics = []
                m_status['values'] = per_value_metrics

            m[status] = m_status

        return m

    @property
    def map_status_function_aggregated(self):
        return {
            _S.added: self.get_stats_default,
            _S.deleted: self.get_stats_default,
            _S.unchanged: self.get_stats_default,
            _S.modified: self.get_stats_default,
        }

    @property
    def map_status_function_per_value(self):
        return {
            _S.unchanged: None,
            _S.added: self.get_per_value_added,
            _S.deleted: self.get_per_value_deleted,
            _S.modified: self.get_per_value_modified,
        }

    def get_stats_default(self, values):
        return {'count': len(values)}

    def get_stats(self, values, status):
        stats = {}

        stats['count'] = values.sum()

        if status in {_S.added, _S.deleted}:
            stats['count']

    def get_colname(self):
        d = {}
        d['colidx'] = self.col_metrics.get_values('colidx')
        d['colname'] = self.col_metrics.get_values('name_header')
        return d

    def get_per_value_added(self, value_properties):
        return {
            'value': value_properties['b_orig'],
            'loc': {'lineno': value_properties['b_lineno'], **self.get_colname()}
        }

    def get_per_value_deleted(self, value_properties):
        return {
            'value': value_properties['a_orig'],
            'loc': {'lineno': value_properties['a_lineno'], **self.get_colname()}
        }

    def get_per_value_modified(self, value_properties):
        vp = value_properties
        m = {}

        m['a'] = {
            'original': vp['a_orig'],
            'calculated_as': vp['a_calc'],
            'loc': {
                'line': vp['a_lineno'],
            }
        }

        m['b'] = {
            'original': vp['b_orig'],
            'calculated_as': vp['b_calc'],
            'loc': {
                'lineno': vp['b_lineno'],
                **self.get_colname(),
            }
        }

        m['delta'] = vp['delta']

        return m


class CSVPlugin(base.Comparator):

    @staticmethod
    def supports():
        return ['csv']

    @classmethod
    def description(cls):
        return cls.__doc__

    def gen_comparison_pairs(self, a, b):
        """
        Return an iterable of (key, comparison_pair), where comparison_pair is a tuple of (item_a, item_b) with a matching key.
        """
        # union of the keys of the two records
        # the ordering of the first record takes precedence
        # an alternative option would be to sort them, lexicographically or with a custom criteria
        keys_union = {**a, **b}.keys()

        for key in keys_union:
            yield key, (a.get(key), b.get(key))

    comment_char = '#'
    calc_options = {
        # 'header_pos': 0,
        # 'index': 'measurement_id',
        # 'index': '',
        # 'dtype': True,
        # 'column_renames': {'date': 'measurement_date'}
    }

    def get_file_metadata(self, src):
        """
        Collect and return file-level metadata.

        Since it's simple, we can do it here rather than in a dedicated class.
        """
        # TODO have to properly decide if Records should be passed a Processor instance or the raw input
        path = Path(src)
        lines = get_lines_frame(path, comment_char=self.comment_char)

        return {
            'path_parent': path.parent,
            'filename': path.name,
            'n_lines': len(lines),
            'n_lines_commented': len(lines[lines['is_comment']]),
            'n_lines_uncommented': len(lines[~lines['is_comment']]),
            'n_chars': lines['content'].str.len().sum(),
        }

    def compare_file(self, src_a, src_b):

        file_md_a = self.get_file_metadata(src_a)
        file_md_b = self.get_file_metadata(src_b)

        metrics = ChangeMetricsBase('file', file_md_a, file_md_b)
        metrics.calculate()

        return dict(metrics)

    def columns_key_getter(self, col_metadata):
        # here the only choice is which col metadata property to use
        # "name", "name_header" and "colidx"
        # TODO consider exposing this as a plug-in-level option (or maybe bool flag?)
        return col_metadata['name']

    def get_record_columns(self, *args, **kwargs):
        """
        Return the Record object used to fetch, process and expose for comparison table columns.
        """
        rec = CSVTableColumnsRecord(*args, comment_char=self.comment_char, **self.calc_options, **kwargs)
        rec.load()
        return rec

    def get_change_metrics_column(self, *args, **kwargs):
        """
        Return the object used to calculate change metrics for table columns.
        """
        return TableColumnChangeMetrics(*args, **kwargs)

    def get_change_metrics_column_values(self, *args, **kwargs):
        """
        Return the object used to calculate change metrics for table column values.
        """
        return TableColumnValuesChangeMetrics.from_column_metrics(*args, **kwargs)

    def compare_table_data(self, src_a, src_b, **kwargs):
        metr_table = {
            'columns': {},
            'values_by_column': {},
        }

        rec_a = self.get_record_columns(src_a)
        rec_b = self.get_record_columns(src_b)

        for comp_key, (col_md_a, col_md_b) in self.gen_comparison_pairs(rec_a, rec_b):
            metr_single_col = self.get_change_metrics_column(comp_key, col_md_a, col_md_b)
            metr_single_col.calculate()

            # series_a, series_b = metr_single_col.get_values('series', orient=tuple)
            # metr_values = self.get_change_metrics_column_values(series_a, series_b)
            metr_values = self.get_change_metrics_column_values(metr_single_col)

            metr_values_data = metr_values.calculate()
            metr_table['values_by_column'][comp_key] = metr_values_data

            metr_single_col.calculate_from_value_metrics(metr_values.table)

            metr_table['columns'][comp_key] = dict(metr_single_col)

        return metr_table

    def compare(self, path_a, path_b, **kwargs):
        self._percent_change = np.nan

        all_metrics = {}

        all_metrics['file'] = self.compare_file(path_a, path_b)

        # col_metrics also contains the value-level metrics as a DataFrame
        # these should be collected separately and merged together in a single table
        all_metrics['table_data'] = self.compare_table_data(path_a, path_b)

        return self.get_processed_metrics(all_metrics)

    def get_processed_metrics(self, metrics):
        return metrics

    def percent_change(self):
        return self._percent_change

    def get_stats_table(self, table_metrics):
        all_cols_stats = []

        for colname, col_metrics in table_metrics['columns'].items():
            col_stats = {'name': colname}
            col_stats.update(col_metrics['values'])
            col_stats['status'] = col_metrics['status']

            all_cols_stats.append(col_stats)

        df = pd.DataFrame(all_cols_stats).set_index('name')

        self._percent_change = df['frac_changed'].mean() * 100

        return df

    def stats(self, changes, detail_level=1):
        from .util import to_json

        df_table = self.get_stats_table(changes['table_data'])

        if detail_level >= 0:
            # single-number change percentage:
            print(f'percent change: {self.percent_change():04.2f}%')

        if detail_level >= 1:
            # overview table with per-column statistics for all columns
            print(df_table)

        if detail_level >= 2:
            # complete change data, assumed to be dict-like (with no assumptions on structure)
            out = to_json(changes)
            print(out)
