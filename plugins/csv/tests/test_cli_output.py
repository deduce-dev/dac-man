import pytest

from ._data import PATH_2, PATHS_2

CLI_NAME = 'dacman-csv'


@pytest.fixture
def cli_args():
    args = []

    config = PATH_2 / 'config.py'

    args += ['--config', config]
    args += PATHS_2

    # script_runner is OK with pathlib.Path objects
    return args


def test_produces_default_output(script_runner, cli_args):

    ret = script_runner.run(CLI_NAME, *cli_args)

    assert ret.success

