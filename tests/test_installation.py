import dacman  # if the config dir is not present, this import will create it


def test_config_directory_is_installed(dir_config):
    assert dir_config.exists()


def test_plugin_config_exists(dir_config):
    assert (dir_config / 'plugins.yaml').exists()


def test_invoking_dacman_with_no_args(script_runner, cli_name):
    """
    This should check whether there's any error in the basic CLI functionality,
    independent of the subcommand.

    TODO at the moment, the error message is printed to stdout. Shouldn't it be to stderr instead?
    """
    ret = script_runner.run(cli_name)

    assert ret.returncode != 0
    # assert cli_name in ret.stdout  # TODO this should be stderr
    # it seems that if using tox, the assertion with stderr will be true,
    # while running the same test from the development virtualenv the one with stdout is true
    # it could be related to the value of the "script_launch_mode" setting of pytest-console-scripts
    # although it seems to be the same in both cases
    # it's probably reasonable to include both cases for the moment and check later
    assert cli_name in ret.stderr or cli_name in ret.stdout
