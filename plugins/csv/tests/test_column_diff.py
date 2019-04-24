from dacman_csv import ColumnDiffer

# TODO this would probably be a good use case for using Hypothesis (with pandas strategies)
import pandas as pd
import numpy as np

import pytest


@pytest.fixture
def columns_simple():
    # these should be fixed, so that we can make position-specific assertions on the output
    old = pd.Series([1, 4, 3, 24, None], index=list('abcdf'))
    new = pd.Series([2, 3, 6, 5, None], index=list('bcdef'))

    return old, new


def test_input_data_has_expected_structure(columns_simple):
    old, new = columns_simple
    df = pd.DataFrame({'old': old, 'new': new})

    pd.testing.assert_index_equal(df.index, old.index | new.index)

    np.testing.assert_equal(df.at['a', 'new'], np.nan)
    np.testing.assert_equal(df.at['e', 'old'], np.nan)

    np.testing.assert_equal(df.at['f', 'old'], np.nan)
    np.testing.assert_equal(df.at['f', 'new'], np.nan)


# TODO the built-in comparators will be tested extensively on their own, but we put them here temporarily
# because they are required by the ColumnDiffer
def _compare_eq(old, new):
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


def _compare_numeric(old, new):
    diff = old - new
    is_changed = diff.abs() > 0.
    return diff, is_changed


def _get_detailed_info(diff):
    """
    How to access the extended comparator outcome data table from the diff object?
    This is an implementation detail, and only used for testing purposes.
    """
    # TODO maybe this should be converted to a proper (interal) API instead
    # i.e. the Diff objects keeps a reference to the object(s) that generated it
    # so that they can be tested
    # this is compatible with the design choice of Diff objects being stateful (as opposed to stateless Differs)
    return diff._table


# using feature from https://docs.pytest.org/en/latest/fixture.html#fixture-parametrize
@pytest.fixture(params=[_compare_eq, _compare_numeric])
def comparator(request):
    return request.param


@pytest.fixture
def diff(comparator, columns_simple):
    differ = ColumnDiffer(comparator=comparator, field='test_field')
    diff = differ(*columns_simple)
    return diff


def test_diff_has_core_components(diff):

    assert diff.added is not None
    assert diff.deleted is not None
    assert diff.changed is not None
    assert diff.unchanged is not None


def test_diff_unchanged(diff):
    assert 'c' in diff.unchanged.index


def test_diff_added(diff):
    assert 'e' in diff.added.index


def test_diff_deleted(diff):
    assert 'a' in diff.deleted.index


@pytest.mark.parametrize('exp_changed', ['b', 'd'])
def test_diff_changed(diff, exp_changed):
    assert exp_changed in diff.changed.index


@pytest.fixture
def expected_status():
    return pd.Series({'a': 'D', 'b': 'C', 'c': 'U', 'd': 'C', 'e': 'A', 'f': 'N'})


def test_diff_status_is_as_expected(diff, expected_status):
    df = _get_detailed_info(diff)
    # important: set `check_categorical` to False (in addition to `check_dtypes`), otherwise it'll fail
    pd.testing.assert_series_equal(
        df['status'],
        expected_status,
        check_dtype=False,
        check_names=False,
        check_categorical=False,
    )


def test_diff_detailed_info_logic_is_as_expected(diff):
    df = _get_detailed_info(diff)

    expected = pd.DataFrame({
            'null_to_notnull': {
                'a': False,
                'b': False,
                'c': False,
                'd': False,
                'e': True,
                'f': False},
            'notnull_to_null': {
                'a': True,
                'b': False,
                'c': False,
                'd': False,
                'e': False,
                'f': False},
            'null_to_null': {
                'a': False,
                'b': False,
                'c': False,
                'd': False,
                'e': False,
                'f': True},
            'both_notnull': {
                'a': False,
                'b': True,
                'c': True,
                'd': True,
                'e': False,
                'f': False}
            })

    pd.testing.assert_frame_equal(
        df[list(expected.keys())],
        expected,
        check_names=False,
    )