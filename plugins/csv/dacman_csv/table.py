from pathlib import Path
import pandas as pd

from . import _base
from . import comparators as builtin_comparators
from .viewers import display_diff_data


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

DEFAULT_COMPARATOR = builtin_comparators.compare_eq


class Differ(_base.Differ):

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

        self.diff_factory = diff_factory or Diff

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
            'compare_eq': builtin_comparators.compare_eq,
            'compare_numeric': builtin_comparators.compare_numeric,
            'compare_time': builtin_comparators.compare_time,
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

        return DiffBuilder(*data_pair)


class Diff(_base.Diff):
    
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


class DiffBuilder(_base.DiffDataClientMixin):

    def __init__(self, *dataframes):
        
        # self.old, self.new = dataframes
        self.data = dataframes

        self.schema_diff = SchemaDiffer().diff_dataframes(*dataframes)
        self.index_diff = IndexDiffer().diff_dataframes(*dataframes)

    # TODO in principle this could be delegated to the Differ, since the main purpose of this object is to manage the diff data state
    # and not the assignment logic
    def get_column_differ(self, comparators, field):
        from . import column

        # TODO this would really benefit from a more clever field-comparator assignation mechanism
        # for the time being, let's use this:
        # if there's an "ANY_KEY" entry in `comparators`, use that, otherwise use the global default
        local_default = comparators.get(ANY_KEY, DEFAULT_COMPARATOR)
        comparator = comparators.get(field, local_default)
        differ = column.Differ(comparator=comparator, field=field)

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
        return DiffStack.from_column_diffs(self.column_diffs)

    def build_values(self):
        self.values_diff = ValuesDiff(self.get_diff_stack())

    def get_diff(self, **kwargs):
        return Diff(schema=self.schema_diff, index=self.index_diff, values=self.values_diff, **kwargs)


class DiffStack:
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


class ValuesDiff(_base.Diff):
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


class SchemaDiffer(_base.Differ):

    # TODO should Differs have their own type dispatcher?
    # e.g. figure out the correct method to use depending on the dtype
    # note that this is similar to what file-level Dispatcher objects would do
    # based on file name/extension.
    # again, the overall hierarchical structure becomes apparent...
    def diff_dataframes(self, df1, df2):
        return self.get_diff(df1.columns, df2.columns)

    def get_diff(self, fields1, fields2):
        return SchemaDiff(fields1, fields2)


class SchemaDiff(_base.Diff):

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
class IndexDiff(_base.Diff):
    
    def __init__(self, *indexes, **kwargs):
        super().__init__(**kwargs)

        old, new = indexes

        self.added = new.difference(old)
        self.deleted = old.difference(new)

        self.unchanged = old.intersection(new)

        # the index/PK by design cannot be modified
        # TODO the only case is for changes indicated explicitly by the user
        self.changed = set()


class IndexDiffer(_base.Differ):
    diff_factory = IndexDiff

    def diff_dataframes(self, df1, df2):
        return self.get_diff(df1.index, df2.index)
