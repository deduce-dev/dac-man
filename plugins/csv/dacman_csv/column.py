import pandas as pd

from . import _base, comparators


class Diff(_base.Diff):

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


class DiffBuilder(_base.DiffBuilder):

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


# TODO this is repeated while we figure out what's the most reasonable way to put it
_DEFAULT_COMPARATOR = comparators.compare_eq


class Differ(_base.Differ):
    
    # TODO it probably makes sense for this to know about the field as well, if only to record it for the context
    def __init__(self, comparator=None, field=None):
        self.comparator = comparator or _DEFAULT_COMPARATOR
        self.field = field

    def get_diff(self, old, new):
        builder = DiffBuilder(old, new)

        builder.apply_comparator(self.comparator)
        # this should just use the state (df) from the builder, and build the Diff by itself?
        # no, because the builder should maintain all stateful information

        # TODO add context
        # TODO need to figure out a way to serialize the comparator
        # name (qualified) + options are necessary
        # the question is whether to do that here or require the comparator to provide the functionality,
        # which limits the flexibility somewhat
        return Diff(builder.get_diff_table(), context={'comparator': self.comparator, 'field': self.field})
