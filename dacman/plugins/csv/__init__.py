from pathlib import Path
from collections import defaultdict

import numpy as np

try:
    import pandas as pd
except ImportError:
    from dacman.core.utils import dispatch_import_error
    dispatch_import_error(module_name='pandas', plugin_name='CSV')

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
    LOC_ORIG_ROW = '_loc_orig_row'
    LOC_ORIG_COL = '_loc_orig_col'

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

    def calculate(self):

        super().calculate(exclude='values_frame')

        if self['status'] == _S.unset:
            self['status'] = _S.unchanged

    def calculate_from_value_metrics(self, value_metrics_table):
        col_metrics_from_value_metrics = self.get_column_metrics_from_values(value_metrics_table)

        if col_metrics_from_value_metrics['frac_changed'] > 0.:
            self.is_modified = True

        self['values'] = col_metrics_from_value_metrics

    def get_column_metrics_from_values(self, metrics_table):
        m = {}
        df = metrics_table

        n_total = len(df)

        m['n_unchanged'] = (df['status'] == _S.unchanged).sum()
        m['n_added'] = (df['status'] == _S.added).sum()
        m['n_deleted'] = (df['status'] == _S.deleted).sum()
        m['n_modified'] = (df['status'] == _S.modified).sum()
        m['n_changed'] = (m['n_added'] + m['n_deleted'] + m['n_modified'])

        m['frac_changed'] = m['n_changed'] / n_total

        if not (df['delta'].isnull().all()):
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


def get_lines_frame(path, comment_char=None):
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


def infer_dtypes(data, converters=None):
    # the order here is relevant: strings representing floats can be read (erroneously) as datetimes,
    # but the reverse is not true, so pd.to_numeric should come first
    converters = converters or [pd.to_numeric, pd.to_datetime]

    if data.dtype == 'object':
        for conv in converters:
            try:
                data = conv(data)
            except (TypeError, ValueError):
                pass
            else:
                break
    
    return data


class ColumnnProcessor:
    """
    Utility class to perform per-column processing and hold data in various formats
    as needed to create the column-level metadata.
    """

    def __init__(self, data_orig, name=None):
        
        self.data_orig = data_orig

        self.data_calc = None

        self.name = name
        self.header = {}

    def process_header(self, data, pos_mapper=None, pos='rel', **kwargs):

        # pos: relative or absolute
        # relative: count from start of subrange
        # absolute: use _loc_orig_row
        indexer = data.iloc
        if pos.startswith('abs'):
            indexer = data.loc

        pos_mapper = pos_mapper or kwargs

        to_drop = []

        for key, pos in pos_mapper.items():
            val = indexer[pos]
            self.header[key] = val
            to_drop.append(pos)

        return data.drop(indexer[to_drop].index)

    def process_rename(self, data, mapper):
        self.name = self.header.get('name', self.name)

        self.name = mapper.get(self.name, self.name)

        if self.name:
            data.name = self.name

        return data

    def process_dtype(self, data, dtype):
        if dtype is True:
            data = infer_dtypes(data)
        else:
            if dtype is None:
                dtype = {}
            data.astype(dtype.get(self.name, data.dtype))
        return data

    def get_values_frame(self, data_orig, data_calc, index=None):
        df = pd.DataFrame({_F.ORIG: data_orig, _F.CALC: data_calc}, index=data_calc.index)
        # print(f'{self.name}: dtypes={df.dtypes}')

        # so here there are three cases for the index:
        # - a data column
        # - orig
        # - none (reset)
        #   - In this case, we don't particularly need to give it a name
        # we can probably manage to express this by resetting the index in all three cases,
        # and then setting the index appropriately
        if isinstance(index, str) and index == 'orig':
            df = df.reset_index().set_index(df.index.name, drop=False)
        elif index is not None:
            df = pd.merge(index, df, how='left', left_index=True, right_index=True).reset_index().set_index(index.name)
        else:
            # we need to be sure that we have the loc_orig_row as a column of this table
            df = df.reset_index()

        return df


class CSVTableColumnsRecord(_BaseRecord):
    """
    Convert a CSV file into a table, and expose a record as Column in the usual way
    """

    def __init__(self,
                 src,
                 comment_char=None,
                 drop_empty_cols=True,
                 table_range=None,
                 header=None,
                 column_renames=None,
                 index=None,
                 dtype=None,
                ):
        self.src = src

        self.comment_char = comment_char
        self.drop_empty_cols = drop_empty_cols
        self.table_range = table_range or {}

        self.header = header or {}
        self.column_renames = column_renames or {}
        self.dtype = dtype
        self.index = index

        self._mapping = {}

    @staticmethod
    def get_lines_frame(path, comment_char=None):
        """Read lines and associated metadata from a file"""
        with Path(path).open() as f:
            lines = pd.DataFrame({'content': list(f)})
            lines['lineno'] = lines.index + 1

        def is_comment(s):
            if comment_char is None:
                # get a series with the same index where all values are False
                return s == np.nan
            return (s
                    .astype(str)
                    .str.startswith(comment_char)
                    )

        lines['is_comment'] = is_comment(lines['content'])

        return lines

    def get_lineno_loadable(self):
        """
        Return a sequence containing the line numbers (1-based) of lines in the source
        that are loadable by the CSV parser.

        This is used to associate table index/rows with their position in the source.
        """

        def is_skipped_by_csv_parser(s):
            # TODO redo this with more robust values
            # (and maybe invert the logic to "is_included" while we're at it)
            return s.astype(str) == '\n'

        # TODO all of this could probably be merged in a regex
        def is_loadable(df):
            return ~(df['is_comment'] | is_skipped_by_csv_parser(df['content']))

        lines = get_lines_frame(self.src, comment_char=self.comment_char)

        return (lines
                [is_loadable]
                ['lineno']
                .to_list()
               )

    def get_table_orig(self, index_col=_F.LOC_ORIG_ROW):
        load_opts = dict(dtype=object, header=None, comment=self.comment_char)

        table_range = {'row_start': 1, 'row_end': None}
        table_range.update(self.table_range)

        row_idx_start = table_range['row_start'] - 1
        row_idx_end = None

        try:
            row_idx_end = table_range['row_end'] - 1
        except TypeError:
            pass

        load_opts['skiprows'] = range(0, row_idx_start)

        if row_idx_end is not None:
            # TODO check for off-by-1 errors
            load_opts['nrows'] = row_idx_end - row_idx_start

        df = pd.read_csv(self.src, **load_opts)

        lineno = self.get_lineno_loadable()[row_idx_start:row_idx_end]

        return (df
                .assign(**{_F.LOC_ORIG_ROW: lineno})
                .set_index(index_col, drop=True)
               )

    def get_metadata(self, col_processor, index=None):
        md = {}

        md['colidx'] = col_processor.colidx
        md['name'] = col_processor.name
        md['header'] = col_processor.header

        md['values_frame'] = col_processor.get_values_frame(col_processor.data_orig,
                                                            col_processor.data_calc,
                                                            index=index)

        return md

    @staticmethod
    def key_getter(metadata):
        return metadata['name']

    # TODO a more detailed name for this could be "get_column_metadata_mapping"
    def get_mapping(self):

        df = self.get_table_orig()

        if self.drop_empty_cols:
            df = df.dropna(axis='columns', how='all')

        processors = []
        index = None

        for col in df:
            proc = ColumnnProcessor(df[col], name=col)
            proc.colidx = col

            proc.data_calc = (proc.data_orig
                              .pipe(proc.process_header, **self.header)
                              .pipe(proc.process_rename, self.column_renames)
                              .pipe(proc.process_dtype, dtype=self.dtype)
                             )

            if proc.name:
                processors.append(proc)

                proc.is_index = (proc.name == self.index)
                if proc.is_index:
                    index = proc.data_calc

        mapping = {}

        for proc in processors:
            md = self.get_metadata(proc, index=index)
            mapping[self.key_getter(md)] = md

        return mapping

    def load(self):
        self._mapping = self.get_mapping()
        # this is just for display/reference, and it's not used for actual calculations
        # self.table_calc = pd.DataFrame({name: md['values_frame']['calc'] for name, md in self._mapping.items()})

    def get_empty(self):
        return {'values_frame': pd.DataFrame([], columns=[_F.ORIG, _F.CALC, _F.LOC_ORIG_ROW])}


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
        self._supports_numeric_delta = None

    @property
    def supports_numeric_delta(self):
        return self._supports_numeric_delta

    def get_table(self):
        values_frames = {'a': self.values_a, 'b': self.values_b}

        concat_opts = {
            'axis': 'columns',
            'join': 'outer',
            'sort': False,
        }

        df = pd.concat(values_frames, **concat_opts)

        # TODO factor out this dtype assignment?
        return (df
                .astype({('a', _F.LOC_ORIG_ROW): 'Int64', ('b', _F.LOC_ORIG_ROW): 'Int64'})
               )

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

        df.loc[:, 'is_equal'] = df[('a', _F.CALC)] == df[('b', _F.CALC)]
        df.loc[:, 'is_null_a'] = df[('a', _F.CALC)].isna()
        df.loc[:, 'is_null_b'] = df[('b', _F.CALC)].isna()
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
            delta = df[('b', _F.CALC)] - df[('a', _F.CALC)]
        except TypeError:
            self._supports_numeric_delta = False
            delta = np.nan
        else:
            self._supports_numeric_delta = True

        df.loc[:, 'delta'] = delta

        return df

    def is_value_modified(self, df):
        epsilon = 1e-6

        if self.supports_numeric_delta:
            return ~df['is_equal'] & (df['delta'].abs() > epsilon)
        return ~df['is_equal']

    def assign_change_status(self, df):
        # TODO additional logic here would be e.g. implementing per-field or per-dtype thresholds
        # TODO make this a categorical
        status = pd.Series(_S.unset, index=df.index)
        status[df['is_null_a'] & (~df['is_null_b'])] = _S.added
        status[(~df['is_null_a']) & df['is_null_b']] = _S.deleted

        status[(~df['is_null_any']) & self.is_value_modified(df)] = _S.modified
        status[status == _S.unset] = _S.unchanged
        df.loc[:, 'status'] = status

        return df

    def get_per_status_metrics(self):
        m = {}

        for status in [_S.unchanged, _S.added, _S.deleted, _S.modified]:
            m_status = {}
            values_with_status = self._table[lambda d: d['status'] == status]
            has_with_status = len(values_with_status) > 0

            if not has_with_status:
                # this "continue" means that change statuses with no values
                # are not added to the metrics at all (as opposed to having `{count: 0}` or similar)
                # it could possibly be exposed as an option
                # depening on what are the requirements for the schema/structure of the output
                continue

            f_aggregated = self.map_status_function_aggregated[status]

            m_status.update(f_aggregated(values_with_status))

            f_per_value = self.map_status_function_per_value[status]

            if f_per_value is not None:
                per_value_metrics = []
                if has_with_status:
                    per_value_metrics = values_with_status.apply(f_per_value, axis=1).to_list()
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

    def get_per_value_added(self, value_properties):
        return {
            'value': value_properties[('b', _F.ORIG)],
            'loc': {'row': value_properties[('b', _F.LOC_ORIG_ROW)]}
        }

    def get_per_value_deleted(self, value_properties):
        return {
            'value': value_properties[('a', _F.ORIG)],
            'loc': {'row': value_properties[('a', _F.LOC_ORIG_ROW)]}
        }

    def get_per_value_modified(self, value_properties):
        vp = value_properties
        m = {}

        def get_m_for_side(d, side):
            return {
                'original': d[(side, _F.ORIG)],
                'calculated_as': d[(side, _F.CALC)],
                'loc': {
                    'row': d[(side, _F.LOC_ORIG_ROW)]
                }
            }
        m['a'] = get_m_for_side(vp, 'a')
        m['b'] = get_m_for_side(vp, 'b')
        # the key must be ('delta', '') instead of only 'delta'
        # otherwise strange and horrible errors (segmentation faults from numpy/pandas) will occur
        # this could be a pandas bug, so it would be good to investigate this in more detail at some point
        if self.supports_numeric_delta:
            m['delta'] = vp[('delta', '')]

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

    record_opts = {}
    comment_char = '#'

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
        rec = CSVTableColumnsRecord(*args, comment_char=self.comment_char, **self.record_opts, **kwargs)
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

        # for each comparison pair of columns from the two tables
        for comp_key, (col_md_a, col_md_b) in self.gen_comparison_pairs(rec_a, rec_b):

            # first, calculate the change metrics for the column as a whole
            metr_single_col = self.get_change_metrics_column(comp_key, col_md_a, col_md_b)
            metr_single_col.calculate()

            # then, calculate the change metrics for the column values
            metr_values = self.get_change_metrics_column_values(metr_single_col)
            metr_values_data = metr_values.calculate()

            # finally, add info about change in values to the column change metrics
            metr_single_col.calculate_from_value_metrics(metr_values.table)

            metr_table['values_by_column'][comp_key] = metr_values_data
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

    detail_level = 1

    def stats(self, changes, detail_level=None):
        from .util import to_json

        detail_level = detail_level or self.detail_level

        df_table = self.get_stats_table(changes['table_data'])

        if detail_level >= 0:
            # single-number change percentage:
            print(f'percent change: {self.percent_change():04.2f}%')

        if detail_level >= 1:
            with pd.option_context('display.max_columns', None):
            # overview table with per-column statistics for all columns
                print(df_table)

        if detail_level >= 2:
            # complete change data, assumed to be dict-like (with no assumptions on structure)
            out = to_json(changes)
            print(out)
