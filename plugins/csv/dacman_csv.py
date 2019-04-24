#!/usr/bin/env python


import pandas as pd

from enum import Enum
import numpy as np


from pathlib import Path
from argparse import ArgumentParser
import json



class DiffAction:
    ADD = 'add'
    DELETE = 'delete'
    CHANGE = 'change'
    # TODO I'm having a hard time to find a verb that's the opposite of "change",
    # meaning "leave unchanged"
    PASS = 'pass'


class DiffUnit:
    ADDED = 'added'
    DELETED = 'deleted'
    CHANGED = 'changed'
    UNCHANGED = 'unchanged'


class BaseDiff:
    """
    The result of a diff operation.

    Some ideas for the interface:
    - Fundamental units/kinds/... (added, deleted, changed, unchanged)
    - Context: information about parameters/options/conditions that affect how the diff is computed

    Other aspects:
    - Serialization: export to record, i.e. dict with base types only (so that it can be exported losslessly to JSON/YAML)
    - Deserialization: recreate losslessly from record
        - This is important if we want to:
            - Use DiffView objects as a base for visualization
            - Use Diff objects as the unified interface, i.e. view = DiffView(diff)
            - Be able to create DiffView objects from serialized Diff objects (i.e. "offline", after the diff was computed)
    """
    # TODO this should rather be component_serializer or something
    # converter = list
    converter_record = list
    converter_display = None

    def __init__(self,
                 added=None, deleted=None, changed=None, unchanged=None,
                 context=None,
                 # TODO maybe this could be included in the context, or in a "metrics" dict, so as to relax the interface a bit
                 data_info=None,
                 factory=list,
                 **kwargs,
    ):
        # TODO this is a bit tedious. Consider wrapping in a class?
        self.added = added if added is not None else factory()
        self.deleted = deleted if deleted is not None else factory()
        self.changed = changed if changed is not None else factory()
        self.unchanged = unchanged if unchanged is not None else factory()

        self.context = context or {}
        # or maybe "context" can be a kitchen sink and include also kwargs?
        self.context.update(**kwargs)

        # TODO is there a reasonable default?
        self.data_info = data_info or {}

        # TODO what's needed to do the analysis?
        # - len(data_old)
        # - len(data_new)
    def to_record(self, converter=None):
        # TODO this probably belongs in the base class,
        # but we have to figure out a smart way for subclasses to extend it

        converter = converter or self.converter_record
        # slightly involved, but in this way we keep the functional flow
        if converter is None:
            converter = lambda x: x

        # TODO to_record values should only contain basic types: decide which ones
        # TODO my guess is that these will generally be lists/arrays. Is it always true?
        d = {
            'added': converter(self.added),
            'deleted': converter(self.deleted),
            'unchanged': converter(self.unchanged),
            'changed': converter(self.changed),
            # '_context': self.context,
        }

        return self.with_context(d)
    
    def with_context(self, d):
        # TODO this should be immutable. But then we have to deepcopy?
        d['_context'] = self.context
        return d

    def __repr__(self):
        return f'<{type(self).__name__}>'

    def display(self):
        from IPython.display import display, display_markdown
        display(str(self))

        display_markdown('added', raw=True)
        display(self.added)
        display_markdown('deleted', raw=True)
        display(self.deleted)
        display_markdown('unchanged', raw=True)
        display(self.unchanged)
        display_markdown('changed', raw=True)
        display(self.changed)

    # to use in Jupyter Notebooks
    def _ipython_display_(self):
        return self.display()

class BaseDiffBuilder:
    """
    I'm not really sure whether this is strictly needed.
    
    The idea is that, in general, we don't want to store the (pre, post) data in the Diff object, in case we want to accumulate them directly.
    However, in some cases, it can be beneficial to store that state in an object while processing the diff (i.e. creating and filling the Diff object),
    which is then discarded (generally, automatically, at te end of differ(pre, post)).

    This class would then be used as an intermediate step in the chain:
    Differ -> DiffBuilder -> Diff

    One alternative would be to have a "heavy" Diff object (holding on the (pre, post) data),
    and let the caller (that in any case is responsible for the accumulation) decide whether to store it directly, or only a view of it:

    Differ -> Diff -> DiffReport/Diff.to_record()
    """


class DiffDataClientMixin:
    """
    Convenience mixin class for classes (typically, but not necessarily, DiffBuilders) mantaining bindings to the diff data.
    """

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data_pair):
        assert len(data_pair) == 2
        self._data = data_pair

    def __iter__(self):
        return iter(self.data)

    @property
    def old(self):
        return self.data[0]

    @property
    def new(self):
        return self.data[1]


class BaseDiffer:
    """
    Implements the general interface f(pre, post) -> Diff

    Any callable matching this signature can be a Differ: this base class is mainly used to store steering parameters (at object instantiation)
    (a similar result can be obtained with currying, e.g. functools.partial).

    One essential property of Differ objects is that they must be stateless with respect to the (pre, post) data, i.e. the same differ instance
    is used to process all (appropriate) change pairs in the changeset.
    """
    diff_factory = BaseDiff

    def get_diff(self, pre, post):
        return self.diff_factory(pre, post)

    def __call__(self, *args):
        return self.get_diff(*args)


class Loader:
    """
    Helper class to streamline and encapsulate the process of loading the data to be diffed from a specified source `io`.

    This class makes no assumption on the relation between the data and the options it manages,
    i.e. if the same object is used to load all data units or not: this is up to the client (the highest-level Differ, i.e. TableDiffer) to decide.
    At the moment TableDiffer supports using a single Loader object with different sources; if need be, this assumption can be relaxed to gain more flexibility
    in case e.g. the two sources to be diffed have different structure, need different processing and so on.
    """
    def __init__(self, io=None, load_func=None, load_opts=None,
                 rename_fields=None,
                 process_func=None,
                 index_fields=None,
                 sort_fields=None,
                 ):

        self.io = io
        self.load_func = load_func or pd.read_csv  # TODO should this be the default?
        # or rather, should the default be set here?
        self.load_opts = load_opts or {}
        
        self.rename_fields = rename_fields or {}
        self.process_func = process_func or (lambda d: d)

        # TODO decide whether to set defaults here or in the client
        self.index_fields = index_fields
        self.sort_fields = sort_fields
        
    def get_data(self, io=None):

        io = io or self.io
        df = (self.load_func(io, **self.load_opts)
              .rename(columns=self.rename_fields)
              .pipe(self.process_func)
             )

        if self.index_fields:
            df = df.set_index(self.index_fields)

        if self.sort_fields:
            # TODO this should also support specifying sort order
            # e.g.[(field_1, ascending_1), (field_2, ascending_2), ...]
            df = df.sort_values(self.sort_fields)
        
        return df


# TODO not sure where this thing belongs: it signifies "any", in the sense of default/fallback
# mostly concerning fields (since they seem to have the largest configuration space), but not exclusively
# since it's essentially config related I guess that the strongest association would be with TableDiffer
ANY_KEY = '*'


# TODO instead of "CSV", probably a better prefix (i.e. less implementation-specific) would be "TabularData/Table"
# this is connected to the deeper question of "at what level we want to analyze the data", i.e. "what are we diffing":
# Roughly, the levels I've identified so far:
# (from less to more information/structure, which also means from less to more preprocessing (-> assumptions) of the data):
# - lines of text 
# - lines of text indexed by one key 
# - list/dict of records (tuples/dicts) 
# - dict of homogeneously-typed columns/arrays 
# - native pandas data structures
# - fully domain-specific data semantics
class TableDiffer(BaseDiffer):

    @classmethod
    def from_config_py(cls, path, **kwargs):
        # TODO dynamically load config file path
        path = Path(path)
        _locals = {}
        with path.open('r') as f:
            exec(f.read(), None, _locals)
        # TODO think about changing the format so that e.g. keys are module-level variables instead of having to use a dict
        config = _locals['CONFIG']

        return cls(config=config, **kwargs)

    def __init__(self,
                 config=None,
                 loader=None,
                 diff_factory=None,
                 display_data=False,
    ):
        # TODO use default config instead?
        self.config = config or {}
        # TODO what to do if loader is somehow in contrast with config?
        self.loader = loader or self.get_loader(self.config)
        self.comparators = self.get_comparators(self.config)

        self.diff_factory = diff_factory or TableDiff

        self.display_data = display_data

    def get_loader(self, config):
        # TODO this smells a bit - probably we can decide once we streamline the config pathway
        # TODO this should be an enum
        load_mode = config.get('load_mode', 'csv')
        map_mode_to_func = {'csv': pd.read_csv, 'excel': pd.read_excel}

        load_func = config.get('load_func', map_mode_to_func[load_mode])

        loader = Loader(
            io=None,  # this will be set in `get_diff()`
            load_func=load_func,
            load_opts=config.get('load_opts'),
            rename_fields=config.get('rename_fields'),
            process_func=config.get('process_func'),
            # TODO index_fields?
            index_fields=config.get('index_fields'),
            sort_fields=config.get('sort_fields'),
        )

        return loader

    def get_comparators(self, config):

        # TODO an explicit table is probably better than trying to locals()[name]
        # also, we could use aliases and so on
        obj_table = {
            'compare_eq': compare_eq,
            'compare_numeric': compare_numeric,
            'compare_time': compare_time,
        }

        # TODO this is probably more general than this, and could go elsewhere
        def get_comparator_obj(obj_or_name):
            if callable(obj_or_name):
                obj = obj_or_name
            else:
                name = obj_or_name
                obj = obj_table.get(name)
            if obj is None:
                pass
                # TODO try to search for it in the dynamically loaded module
                # or is it better to update the obj_table and search there?
            return obj

        # TODO think where it would be the best place to insert those complicated rules to assign comparators based on the fields
        # (and, in general, if it makes sense or not)
        input_ = config.get('comparators', {})

        objs = {key: get_comparator_obj(comparator) for key, comparator in input_.items()}

        return objs

    def get_data(self, *files):
        # TODO adapt to use two different loaders
        return [self.loader.get_data(file) for file in files]

    @property
    def params(self):
        # config options: all of these are part of the diff context, at various levels
        # I should pass these to the diff or the builder
        # TODO if we want to support different loaders, then we'll have to rethink this structure
        return dict(self.config)

    def get_diff(self, *files):
        # data_pair = self.get_data(*files)
        # return self.diff_factory(*data_pair)
        builder = self.get_builder(*files)
        builder.build_columns(comparators=self.comparators)
        builder.build_values()
        # TODO obviously this is not the right place to do this conversion
        # and probably, it should go directly to the JSON/YAML serializer (for json.JSONEncoder, that would be a custom `default` function)
        return builder.get_diff(context={'old': str(files[0]), 'new': str(files[1]), 'config': self.params})

    def get_builder(self, *args, **kwargs):
        data_pair = self.get_data(*args)

        if self.display_data:
            display_diff_data(*data_pair)

        return TableDiffBuilder(*data_pair)


# TODO strongly consider about using a flat structure to expose the subcomponents (schema, index, records, ...)
class TableDiff(BaseDiff):
    
    # TODO should we hard-code the components?
    # TODO this is a case of "composite" Diff. Is this peculiar/common enough to be worth a proper concept/interface?
    # it sure is a pain in the rear to deal with all this repetition...
    def __init__(self, schema=None, index=None, values=None, **kwargs):
        super().__init__(**kwargs)

        self.schema = schema
        self.index = index
        self.values = values

        self.added = {
            'schema': self.schema.added,
            'index': self.index.added,
            'values': self.values.added,
        }

        self.deleted = {
            'schema': self.schema.deleted,
            'index': self.index.deleted,
            'values': self.values.deleted,
        }

        self.unchanged = {
            'schema': self.schema.unchanged,
            'index': self.index.unchanged,
            'values': self.values.unchanged,
        }

        self.changed = {
            'schema': self.schema.changed,
            'index': self.index.changed,
            'values': self.values.changed,
        }

    @property
    def components(self):
        yield self.schema
        yield self.index
        yield self.values

    def to_record(self):
        names = ['schema', 'index', 'values']
        d = {name: component.to_record()
                for name, component in zip(names, self.components)
            }

        return self.with_context(d)
    # def converter(self, group):
    #     print(group)
    #     return {key: list(val) for key, val in group.items()}


# should the builder be responsible for assembling the partial results?
# i.e. for levels of equal or greater depth?
class TableDiffBuilder(DiffDataClientMixin):

    def __init__(self, *dataframes):
        
        # self.old, self.new = dataframes
        self.data = dataframes

        self.schema_diff = TableSchemaDiffer().diff_dataframes(*dataframes)
        self.index_diff = TableIndexDiffer().diff_dataframes(*dataframes)

    # TODO in principle this could be delegated to the differ, since the main purpose of this object is to manage the diff data state
    # and not the assignment logic
    def get_column_differ(self, comparators, field):
        # TODO this would really benefit from a more clever field-comparator assignation mechanism
        # for the time being, let's use this:
        # if there's an "ANY_KEY" entry in `comparators`, use that, otherwise use the global default
        local_default = comparators.get(ANY_KEY, DEFAULT_COMPARATOR)
        comparator = comparators.get(field, local_default)
        differ = ColumnDiffer(comparator=comparator, field=field)

        return differ

    def build_columns(self, comparators):
        fields = self.schema_diff.unchanged

        # at the moment this is just a bare dict {field: column_diff}
        # TODO think how to structure it better (do we need a Column*s*Diff, i.e. for all Columns?)
        # my impression is that it doesn't have to be very fancy, and a list (or dict keyed on field) would suffice
        results = {}

        for field in fields:
            # TODO set up this as a log
            print(f'processing {repr(field)}')

            differ = self.get_column_differ(comparators, field)

            try:
                old, new = [df[field] for df in self.data]
                diff = differ(old, new)
            # possible errors are:
            # - df[field] raises KeyError: by design, this shouldn't happen, and could indicate a previous issue when defining "fields"
            # - something wrong happens in differ: in that case, this should decide whether to skip or raise
            except KeyError as e:
                # for the time being, we just re-raise it
                raise e
            else:
                results[field] = diff

        # TODO if we leave this as a simple dict, it should really be "column_diffs" (a collection of ColumnDiff objects) instead of "columns_diff",
        # which suggests that it's a cohesive Diff object targeting columns
        self.column_diffs = results
        # temporarily leaving this as an alias, until I check and verify that we can remove it
        self.columns_diff = self.column_diffs

    def get_diff_stack(self):
        return TableDiffStack.from_column_diffs(self.column_diffs)

    def build_values(self):
        self.values_diff = TableValuesDiff(self.get_diff_stack())


    def build_records(self):
        comparison_fields = self.schema_diff.unchanged
        # or maybe the builder should take care of the comparison fields?
        builder = TableRecordsDiffBuilder.from_unmatched_dataframes(self.old, self.new, fields=comparison_fields)
        # not sure if we need this binding, let's keep this here for testing
        self.records_builder = builder

        builder.set_from_index_diff(self.index_diff)
        builder.calc_changes()
        # TODO this explicit conversion here is a bit ugly, this should be done in the Diff
        self.records_diff = builder.get_diff(context={
            'comparison_fields': list(comparison_fields)}
        )

    def get_diff(self, **kwargs):
        return TableDiff(schema=self.schema_diff, index=self.index_diff, values=self.values_diff, **kwargs)


class TableDiffStack:
    """
    A 3-axes representation of a table's diff output.

    Each layer has the shape of the table (index, fields), while the third axis holds the various possible views of the Diff.
    """

    VIEWS = ['old', 'new', 'difference', 'status']

    @classmethod
    def from_column_diffs(cls, column_diffs):
        return cls({view_key: pd.DataFrame({field: diff._table[view_key]
                                           for field, diff in column_diffs.items()}).dropna(axis='index', how='all')
                    for view_key in cls.VIEWS
                   })

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()


class TableValuesDiff(BaseDiff):
    """
    Minimal Diff class storing changes to individual values in a table.
    """

    @staticmethod
    def _filter_status(s, status=None, any_of=None):
        # TODO move this as appropriate if we use this status table paradigm elsewhere
        # TODO is there any case where we would need to query multiple values as well?
        if status is not None:
            match = s == status
        elif any_of is not None:
            match = s.isin(any_of)

        return s[match]

    def __init__(self, diff_stack, **kwargs):
        super().__init__(**kwargs)

        self._stack = diff_stack

        self._status = self._stack['status'].stack().sort_values()

        # TODO if we want to have more information we should take care of this,
        # e.g. use the index to query self._stack instead of storing it directly
        def get_values(s):
            return s.index.to_list()

        self.deleted = self._filter_status(self._status, "D").pipe(get_values)
        self.added = self._filter_status(self._status, "A").pipe(get_values)
        self.changed = self._filter_status(self._status, "C").pipe(get_values)
        self.unchanged = self._filter_status(self._status, any_of=["U", "N"]).pipe(get_values)


class TableSchemaDiffer(BaseDiffer):

    # TODO should Differs have their own type dispatcher?
    # e.g. figure out the correct method to use depending on the dtype
    # note that this is similar to what file-level Dispatcher objects would do
    # based on file name/extension.
    # again, the overall hierarchical structure becomes apparent...
    def diff_dataframes(self, df1, df2):
        return self.get_diff(df1.columns, df2.columns)

    def get_diff(self, fields1, fields2):
        return TableSchemaDiff(fields1, fields2)


class TableSchemaDiff(BaseDiff):

    def __init__(self, *fieldsets, **kwargs):
        super().__init__(**kwargs)
        # self.fieldsets = fieldsets
        old, new = fieldsets

        self.added = new.difference(old)
        self.deleted = old.difference(new)
        self.unchanged = old.intersection(new)

        # TODO for the time being we're leaving this empty
        # we can think of smarter strategies (e.g. fuzzy matching)
        # to infer the most likely field renames
        # TODO add changes indicated explicitly by the user
        self.changed = set()



# NOTE this is "the set of changes to the index", not "the index of things (i.e. records/rows) that changed"
# tricky but fundamental difference
class TableIndexDiff(BaseDiff):
    
    def __init__(self, *indexes, **kwargs):
        super().__init__(**kwargs)

        old, new = indexes

        self.added = new.difference(old)
        self.deleted = old.difference(new)

        self.unchanged = old.intersection(new)

        # the index/PK by design cannot be modified
        # TODO the only case is for changes indicated explicitly by the user
        self.changed = set()


class TableIndexDiffer(BaseDiffer):
    diff_factory = TableIndexDiff

    def diff_dataframes(self, df1, df2):
        return self.get_diff(df1.index, df2.index)


def get_changelist(*dataframes, diff_names=None, axes_names=None):
    """
    Build "changelist" table, a dataframe where each row is a change and fields are change attributes.
    """
    diff_names = diff_names or ('old', 'new')

    # TODO refactor the index name assignation
    # Toughts:
    #    - If index fields are not specified, we should assign a name to the index when creating the df
    #    - For multi-column indexes, think if we want to keep the names, or it makes more sense to
    #      treat them more "anonymously"
    test_idx = dataframes[0].index
    if test_idx.nlevels == 1:
        row_axis_names = test_idx.name or ['row_id']
    else:
        row_axis_names = test_idx.names or [f'row_id_{i}' for i in range(test_idx.nlevels)]

    column_name = 'column_id'

    axes_names = axes_names or row_axis_names + [column_name]

    df = (pd.concat(dataframes, axis=1, keys=diff_names)
          .stack()
          # here we should apply the difference calculation first,
          # since we could then tweak the tolerance parameter
          # the issue is that the processing would be done row-wise, and thus inevitably slow
          # the alternative is to do these calculations before stacking
          [lambda d: d[diff_names[0]] != d[diff_names[1]]]
          .rename_axis(axes_names)
          .reset_index()
    )

    return df


# TODO still didn't figure out if this should go in the Diff or in the Builder...
# maybe we could solve this as follows: 
#   - Diff objects should not store the raw, uncompressed data
#   - But they should analyze the data they have (i.e. the diff information). ?...
class TableRecordsDiffBuilder(DiffDataClientMixin):

    @classmethod
    def from_unmatched_dataframes(cls, *dataframes, fields=None):
        return cls(*[df[fields] for df in dataframes])

    def __init__(self, *dataframes):
        self.data = dataframes
        # self.index_diff = index_diff

    def set_from_index_diff(self, index_diff):
        self.added = self.new.loc[index_diff.added]
        self.deleted = self.old.loc[index_diff.deleted]

        self.common_index = index_diff.unchanged

    def calc_changes(self):
        # just trying how the syntax would look like using enums/constants/attributes for (new, old)
        # self.data[OLD].loc[self.common_index] != self.data[NEW].loc[self.common_index]
        # self.data.old.loc[self.common_index] != self.data.new.loc[self.common_index]
        self.changemask_values = self.old.loc[self.common_index] != self.new.loc[self.common_index]
        self.changemask_rows = self.changemask_values.apply(np.any, axis=1)

        self.unchanged = self.new[~self.changemask_rows]
        # and at this point, we go one level deeper and calculate the data changes
        # which means that this requires a list of n_cols ColumnDiffers and/or n_rows Row/RecordDiffers
        self.changed = self.get_changelist_values()

    def get_changelist_values(self):
        return get_changelist(self.old.loc[self.common_index],
                              self.new.loc[self.common_index],
                              diff_names=['old_value', 'new_value']
                             )
        # raise NotImplementedError

    def get_diff(self, **kwargs):
        return TableRecordsDiff(
            added=self.added,
            deleted=self.deleted,
            unchanged=self.unchanged,
            changed=self.changed,
            **kwargs
        )

class TableRecordsDiff(BaseDiff):
    """
    Computes diff for the whole set of records, i.e. the table data,
    differently from 1) the table schema 2) changes in individual table records/rows, or columns.

    The main diff criteria is the primary key/index.
    """
    
    def converter_record(self, component):
        return component.to_dict(orient='records')


class TableRecordsDiffer(BaseDiffer):
    pass


class ColumnDiff(BaseDiff):

    @staticmethod
    def _filter_status(df, status=None, any_of=None):
        # TODO move this as appropriate if we use this status table paradigm elsewhere
        # TODO is there any case where we would need to query multiple values as well?
        if status is not None:
            match = df['status'] == status
        elif any_of is not None:
            match = df['status'].isin(any_of)

        return df[match]

    def __init__(self, table, **kwargs):
    
        super().__init__(self, **kwargs)
        
        # TODO how "official" we want to make this table? decide after taking into account other Diff classes as well
        # TODO also, decide (here?) which columns to keep
        self._table = table

        subset_cols = ['new', 'old', 'difference', 'status']
        subset = table[subset_cols]

        self.added = self._filter_status(subset, "A")
        self.deleted = self._filter_status(subset, "D")
        self.changed = self._filter_status(subset, "C")
        # TODO the decision whether to consider null-to-null as unchanged could take place at this point
        self.unchanged = self._filter_status(subset, any_of=["U", "N"])

    # TODO add converters for to_record


class ColumnDiffBuilder:

    def __init__(self, old, new):
        # creating a dataframe from the passed columns will align their indices properly
        # (or fail if not possible)
        # TODO think of where would be the best place to handle potential failures
        self.df = pd.DataFrame({'old': old, 'new': new})

        # TODO DataFrame column keys should probably be constants instead of hard-coded values
        # the same applies to most other essential strings in the codebase
        # question: would it be better to use enums or simply string constants?

    def apply_comparator(self, comparator):
        to_compare = self.df
        
        difference, is_changed = comparator(to_compare['old'], to_compare['new'])

        self.df['difference'] = difference
        self.df['is_changed'] = is_changed

        self.df = self.assign_difference_properties(self.df)

    def assign_difference_properties(self, df):

        null_to_notnull = df['old'].isnull() & df['new'].notnull()
        notnull_to_null = df['old'].notnull() & df['new'].isnull()
        null_to_null = df['old'].isnull() & df['new'].isnull()
        both_notnull = df['old'].notnull() & df['new'].notnull()

        is_difference_notnull = df['difference'].notnull()
        # using fillna() is necessary because is_changed is boolean, and thus ambiguous with .notnull()
        # astype(bool) should happen automatically, but we explicitly try being strict
        is_changed_proper = df['is_changed'].fillna(False).astype(bool, errors='raise')

        # TODO generally all these names are so ambiguous, maybe we should just use some codes instead for the sake of clarity...
        is_changed_strict = both_notnull & is_changed_proper
        is_unchanged_strict = both_notnull & ~is_changed_proper

        return df.assign(**{
            'null_to_notnull': null_to_notnull,
            'notnull_to_null': notnull_to_null,
            'null_to_null': null_to_null,
            'both_notnull': both_notnull,
            'is_difference_notnull': is_difference_notnull,
            # do we need this as well?
            # 'is_changed_proper': is_changed_proper,
            'is_changed_strict': is_changed_strict,
            'is_unchanged_strict': is_unchanged_strict,
        })

    def assign_diff_status(self, df):
        # TODO change all bare string keys to constants/enums

        # TODO if we extend this status column to other tables, it'll make sense to DRY away the creation of the dtype
        status = pd.Series("UNSET", index=df.index, dtype=pd.CategoricalDtype(["UNSET", "D", "A", "C", "U", "N"]))

        # TODO I realize this is not exactly a critical issue... but it would be nice to think about
        # setting the order consistently for basic diff status/key/type, i.e. DELETED, ADDED, CHANGED, UNCHANGED

        # TODO would it make sense ot check that the properties are mutually exclusive before setting the status?
        status.loc[df['null_to_notnull']] = "A"
        status.loc[df['notnull_to_null']] = "D"

        # TODO there are be cases where the difference is notnull even when one of the data is null
        # (this depends entirely on the comparator, and we're trying to keep the validation here as much as possible)
        # so it would probably make sense to have this use the explicit both_notnull instead
        # OTOH, using difference.notnull() allows the comparator more freedom on how to interpret the results
        # TODO should we expose a config option to set this behavior?
        # if not, just use "is_difference_notnull" instead of "both_notnull"
        status.loc[df['is_changed_strict']] = "C"
        status.loc[df['is_unchanged_strict']] = "U"

        # use a separate status for null-to-null, while we figure out what's the best way to treat it
        status.loc[df['null_to_null']] = "N"

        # avoid changing the df in-place
        return df.assign(**{'status': status})
    
    def get_diff_table(self):
        return self.assign_diff_status(self.df)

    # TODO decide whether to keep this all-in-one version, or separate setting the properties from assigning the status
    def get_diff_table_1(self, df):
        # TODO change all bare string keys to constants/enums

        # TODO if we extend this status column to other tables, it'll make sense to DRY away the creation of the dtype
        status = pd.Series("UNSET", index=df.index, dtype=pd.CategoricalDtype(["UNSET", "D", "A", "C", "U", "N"]))

        # TODO for the purpose of testing/debugging, all of these criteria could be saved in an intermediate table
        null_to_notnull = df['old'].isnull() & df['new'].notnull()
        notnull_to_null = df['old'].notnull() & df['new'].notnull()
        null_to_null = df['old'].isnull() & df['new'].isnull()

        # TODO check this - there might be cases where the difference is notnull even when one of the data is null
        # (this depends entirely on the comparator, and we're trying to keep the validation here as much as possible)
        # so it would probably make sense to have this use the explicit both_notnull instead
        # OTOH, using difference.notnull() allows the comparator more freedom on how to interpret the results
        is_difference_defined = df['difference'].notnull()
        # using fillna() is necessary because is_changed is boolean, and thus ambiguous with .notnull()
        # astype(bool) should happen automatically, but we explicitly try being strict
        is_changed_proper = df['is_changed'].fillna(False).astype(bool, errors='raise')

        # TODO I realize this is not exactly a critical issue... but it would be nice to think about
        # setting the order consistently for basic diff status/key/type, i.e. DELETED, ADDED, CHANGED, UNCHANGED
        status.loc[null_to_notnull] = "A"
        status.loc[notnull_to_null] = "D"

        status.loc[is_difference_defined & is_changed_proper] = "C"
        status.loc[is_difference_defined & ~is_changed_proper] = "U"

        # use a separate status for null-to-null, while we figure out what's the best way to treat it
        status.loc[null_to_null] = "N"

        # avoid changing the df in-place
        return df.assign(**{'status': status})



# TODO move these to their own module
def compare_eq(old, new):
    # TODO this is supposed to be the defaul/fallback comparator
    # but it still depends on how (old, new) implement __eq__
    # specifically for pandas dtypes, there are some gotchas that we should account for
    # e.g. comparing categoricals with different categories is not allowed by default
    
    # this will be "True" if either value is NaN, and also if both values are NaNs
    # which is different from what one could expect, especially if the original values are the same
    # the question is what would be the best place to set this logic
    is_changed = (old != new)
    # this returns 1. (100% change) if is_changed == True, or 0. if not
    diff = is_changed.astype(float)
    return diff, is_changed


def compare_numeric(old, new):
    diff = old - new
    is_changed = diff.abs() > 0.
    return diff, is_changed


def compare_time(old, new):
    diff = old - new
    is_changed = diff.abs() > pd.to_timedelta(0.)
    return diff, is_changed


DEFAULT_COMPARATOR = compare_eq



class ColumnDiffer(BaseDiffer):
    
    # TODO it probably makes sense for this to know about the field as well, if only to record it for the context
    def __init__(self, comparator=None, field=None):
        self.comparator = comparator or DEFAULT_COMPARATOR
        self.field = field

    def get_diff(self, old, new):
        builder = ColumnDiffBuilder(old, new)

        builder.apply_comparator(self.comparator)
        # this should just use the state (df) from the builder, and build the Diff by itself?
        # no, because the builder should maintain all stateful information

        # TODO add context
        # TODO need to figure out a way to serialize the comparator
        # name (qualified) + options are necessary
        # the question is whether to do that here or require the comparator to provide the functionality,
        # which limits the flexibility somewhat
        return ColumnDiff(builder.get_diff_table(), context={'comparator': self.comparator, 'field': self.field})


class BaseDiffViewer:
    
    def __init__(self, diff=None, **kwargs):
        self.diff = diff


class ExtendedJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        import os

        if isinstance(obj, os.PathLike):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        # this should cover most of our needs regarding functions
        if callable(obj):
            return str(obj)

        return super().default(obj)


class PrettyPrint(BaseDiffViewer):
    
    def __init__(self, diff=None, backend='json', **kwargs):
        self.diff = diff
        self.backend = backend

    def render(self):
        if self.backend == 'json':
            return json.dumps(self.diff.to_record(), indent=4, separators=(', ', ': '), cls=ExtendedJSONEncoder)

    def __repr__(self):
        return self.render()


class Interactive(BaseDiffViewer):

    @property
    def stack(self):
        return self.diff.values._stack

    def apply_status_color(self, df):
    
        status = self.stack['status'].loc[df.index, df.columns]
    
        status_prop_map = {
            # TODO rethink color palette, especially in terms of accessibility
            'C': 'background-color: #ffff99',
            'D': 'background-color: #ffad99',
            'A': 'background-color: #99ff99',
            'N': 'background-color: #cccccc',
            'U': '',
        }

        return status.apply(lambda c: c.map(status_prop_map), axis=0)

    def get_style(self, df):
        return (df
                .dropna(axis='index', how='all')
                .style
                .apply(self.apply_status_color, axis=None)
                )

    def get_stack_style(self):
        return {field: self.get_style(df)
                for field, df in self.stack.items()}

    def get_view_selector(self):
        from ipywidgets import widgets
        return widgets.ToggleButtons(
            options=['old', 'new', 'difference', 'status'],
            description='View: ',
            disabled=False,
            button_style='', 
        )

    def get_sort_selector(self):
        from ipywidgets import widgets

        return widgets.Dropdown(
            options=self.diff.schema.unchanged,
            value=None,
            description='Sort by: ',
        )

    def _ipython_display_(self):
        from IPython.display import display

        display(self.display())

    def display(self):
        from IPython.display import display
        from ipywidgets import widgets

        def f(sort_by=None, key=None):
            # df = self.get_stack_style()[]
            df = (self.stack[key]
                  .dropna(axis='index', how='all')
            )
            if sort_by:
                df = df.sort_values(sort_by)

            df.drop
            display(df.pipe(self.get_style))

        interactive_output = widgets.interactive(f, 
            sort_by=self.get_sort_selector(),
            key=self.get_view_selector(),
        )

        output = interactive_output.children[-1]
        output.layout.height = '700px'
        return interactive_output


# TODO maybe at some point it will make sense to have a lightweight DiffData class
def display_diff_data(old, new):
    from IPython.display import display, display_pretty

    print('displaying diff data:')
    print('old:')
    display(old)
    print('new:')
    display(new)


def get_cli_parser():
    """
    Create and setup the parser to process the CLI arguments.
    """
    parser = ArgumentParser()
    # using the `type` kwarg is used to automatically validate the parsed value at the CLI invocation stage
    # invalid values result in an immediate Argparse exception (i.e. the same as providing invalid flags)
    parser.add_argument('old', type=Path, help='path to old file')
    parser.add_argument('new', type=Path, help='path to new file')
    parser.add_argument('-f', '--format', type=str, required=False, choices=['json'], default='json', help='output format of the diff')
    parser.add_argument('-c', '--config', required=False, default=None, help='path to configuration file')

    return parser


def main():
    parser = get_cli_parser()
    args = parser.parse_args()

    old, new = args.old, args.new
    format_ = args.format

    config = args.config

    if config:
        differ = TableDiffer.from_config_py(Path(config))
    else:
        differ = TableDiffer()

    diff = differ(old, new)
    diff_record = diff.to_record()

    if format_ == 'json':
        # TODO move this to appropriate DiffView class
        output = json.dumps(diff_record, indent=4, separators=(', ', ': '))
        print(output)

if __name__ == "__main__":
    main()