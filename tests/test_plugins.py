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
    return dacman_args + ['--script', script_name]


def is_plugin_used(plugin_name, text):
    return 'comparator plugin = {}'.format(plugin_name) in text


def test_builtin_plugin_is_used_on_matching_files_by_default(script_runner, dir_test, dacman_args):
    res = script_runner.run(*dacman_args, cwd=dir_test)

    assert is_plugin_used('CSVPlugin', res.stdout)


def test_custom_script_is_used_instead_of_builtin_plugin(script_runner, dir_test,
                                                         dacman_args_with_script, script_name):

    res = script_runner.run(*dacman_args_with_script, cwd=dir_test)
    assert is_plugin_used(script_name, res.stdout)


def is_correct_plugin_used_for_files(log_text, path_a, path_b, plugin_name):

    def contains_correct_plugin_info(line, path_a, path_b, plugin_name):
        conditions = [
            str(path_a) in line,
            str(path_b) in line,
            f'using {plugin_name}' in line,
        ]

        return all(conditions)

    lines = log_text.split('\n')
    matches = [line for line in lines if contains_correct_plugin_info(line, path_a, path_b, plugin_name)]
    # there should be exactly one line for a given paths/plugin combination
    print([line for line in lines if plugin_name in line])
    return len(matches) == 1


@pytest.fixture
def dir_data_all_plugins(dir_examples):
    "The directory containing the two example sub-directories with files supported by the built-in plugins"

    return dir_examples / 'data' / 'plugin_test'


@pytest.mark.parametrize("path_a,path_b,plugin_name",[
                         ('v0/table.csv', 'v1/table.csv', 'CSVPlugin'),
                         ('v0/foo.h5', 'v1/foo.h5', 'HDF5Plugin'),
                         ('v0/workbook.xlsx', 'v1/workbook.xlsx', 'ExcelPlugin'),
])
def test_builtin_plugins_are_used_automatically_for_corresponding_file_type(script_runner,
                                                                            dir_data_all_plugins,
                                                                            path_a, path_b, plugin_name):

    res = script_runner.run('dacman', 'diff', '--datachange', path_a, path_b, cwd=dir_data_all_plugins)

    assert is_correct_plugin_used_for_files(res.stdout, path_a, path_b, plugin_name)
