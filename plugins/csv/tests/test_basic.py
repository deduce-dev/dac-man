"""
Test basic functionality using simplest (human-viewable and -writable) data.
"""

import pytest
from dacman_csv import TableDiffer

# TODO maybe this will make sense as a fixture
from ._data import PATHS_BASIC
OLD, NEW = PATHS_BASIC

# TODO with this kind of simple data, we should probably be able to write all diffs by hand
# this can be done once we stabilize/formalize the diff format/interface


@pytest.fixture
def diff():
    differ = TableDiffer()
    return differ(OLD, NEW)

def test_diff_is_not_empty(diff):

    diff_record = diff.to_record()

    assert diff_record  # is not empty

# these should be moved somewhere a bit more general
@pytest.mark.parametrize('name', [
    'added',
    'deleted',
    'changed',
    'unchanged',
])
def test_diff_record_contains_core_diff_attribute(diff, name):
    assert getattr(diff, name, None) is not None

def test_diff_contains_input_file_info(diff):
    
    diff_record = diff.to_record()
    # TODO we will need to change this once we settle on a common interface
    meta = diff_record['_context']

    assert meta['old'] == str(OLD), meta['old']
    assert meta['new'] == str(NEW), meta['new']
