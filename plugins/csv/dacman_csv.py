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
        builder.build_records()
        # TODO obviously this is not the right place to do this conversion
        return builder.get_diff(context={'old': str(files[0]), 'new': str(files[1]), 'diff_params': self.params})

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
    def __init__(self, schema=None, index=None, records=None, **kwargs):
        super().__init__(**kwargs)

        self.schema = schema
        self.index = index
        self.records = records

        self.added = {
            'schema': self.schema.added,
            'index': self.index.added,
            'records': self.records.added,
        }

        self.deleted = {
            'schema': self.schema.deleted,
            'index': self.index.deleted,
            'records': self.records.deleted,
        }

        self.unchanged = {
            'schema': self.schema.unchanged,
            'index': self.index.unchanged,
            'records': self.records.unchanged,
        }

        self.changed = {
            'schema': self.schema.changed,
            'index': self.index.changed,
            'records': self.records.changed,
        }

    @property
    def components(self):
        yield self.schema
        yield self.index
        yield self.records

    def to_record(self):
        names = ['schema', 'index', 'records']
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
        return TableDiff(schema=self.schema_diff, index=self.index_diff, records=self.records_diff, **kwargs)


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


class TableColumnDiffer(BaseDiffer):
    pass


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