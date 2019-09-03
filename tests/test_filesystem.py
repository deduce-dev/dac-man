import pytest


@pytest.fixture
def dacman_args():
    return ['dacman', 'diff', 'v0', 'v1']


@pytest.fixture
def working_dir(dir_examples):
    return dir_examples / 'data/simple'


def test_diff_default_mode(script_runner, working_dir, dacman_args):

    res = script_runner.run(*dacman_args, cwd=working_dir)

    assert 'Diff completed' in res.stdout


def test_diff_with_data_comparison(script_runner, working_dir, dacman_args):
    dacman_args += ['--detailed']

    res = script_runner.run(*dacman_args, cwd=working_dir)

    assert 'Data comparison complete' in res.stdout
    assert 'Diff completed' in res.stdout
