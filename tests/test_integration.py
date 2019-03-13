"""
A series of basic integration tests ensuring that the overall application is working.

Testing the `dacman` CLI is based on the pytest-console-scripts (https://github.com/kvas-it/pytest-console-scripts/) plugin for pytest
"""

CLI_NAME = 'dacman'


def test_cli_with_simplest_action(script_runner):
    """
    The simplest action should allow us to see whether there's any error in the basic CLI functionality,
    independent of the subcommand.

    TODO at the moment, the error message is printed to stdout. Shouldn't it be to stderr instead?
    """
    ret = script_runner.run(CLI_NAME)

    assert ret.returncode != 0
    # assert CLI_NAME in ret.stdout  # TODO this should be stderr
    # it seems that if using tox, the assertion with stderr will be true,
    # while running the same test from the development virtualenv the one with stdout is true
    # it could be related to the value of the "script_launch_mode" setting of pytest-console-scripts
    # although it seems to be the same in both cases
    # it's probably reasonable to include both cases for the moment and check later
    assert CLI_NAME in ret.stderr or CLI_NAME in ret.stdout
