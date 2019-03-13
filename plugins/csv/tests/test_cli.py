CLI_NAME = 'dacman-csv'


def test_with_no_args_error_with_usage(script_runner):

    ret = script_runner.run(CLI_NAME)

    assert not ret.success
    assert CLI_NAME in ret.stderr
    # TODO this can be argparse-dependent
    assert 'arguments are required' in ret.stderr

