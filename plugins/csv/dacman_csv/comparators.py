import pandas as pd


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
