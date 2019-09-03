"""
Checks basic plug-in/script functionality.

We use CSV files for this implementation of the test,
but the features being tested are the same for any plug-in.
"""

import pytest


@pytest.fixture
def dir_test(dir_examples):
    return dir_examples / 'csv'


@pytest.fixture(scope='module')
def dacman_args():
    return ['dacman', 'diff', 'A.csv', 'B.csv']


@pytest.fixture
def script_name():
    return 'my_csv_ana.py'


@pytest.fixture
def dacman_args_with_script(dacman_args, script_name):
    return dacman_args + ['--plugin', script_name]


def is_plugin_used(plugin_name, text):
    return 'comparator plugin = {}'.format(plugin_name) in text


def test_builtin_plugin_is_used_on_matching_files_by_default(script_runner, dir_test, dacman_args):
    res = script_runner.run(*dacman_args, cwd=dir_test)

    assert is_plugin_used('CSVPlugin', res.stdout)


def test_custom_script_is_used_instead_of_builtin_plugin(script_runner, dir_test,
                                                         dacman_args_with_script, script_name):

    res = script_runner.run(*dacman_args_with_script, cwd=dir_test)
    assert is_plugin_used(script_name, res.stdout)

