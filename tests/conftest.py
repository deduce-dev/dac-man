import pytest

from pathlib import Path
import yaml
import logging


@pytest.fixture
def dir_examples(request):
    tests_dir = Path(request.fspath).parent
    return tests_dir.parent / 'examples'


@pytest.fixture(scope='session')
def dir_config():
    return Path.home() / '.dacman/config'


@pytest.fixture(scope='session')
def cli_name():
    return 'dacman'


@pytest.fixture(scope='session')
def logging_config_path(dir_config):
    return dir_config / 'logging.yaml'


@pytest.fixture(autouse=True, scope='session')
def setup_logging(logging_config_path):
    """
    Setup logging for use in tests, e.g. setting it to be more verbose than normal
    overriding the default config.
    """
    with logging_config_path.open() as f:
        old_cfg = yaml.safe_load(f)

    cfg = dict(old_cfg)
    cfg['handlers']['console']['level'] = 'DEBUG'

    # the modified log config must be written to file
    # to be applied for tests that run dacman in a subprocess
    # (like most of the tests currently in this test suite)
    with logging_config_path.open('w') as f:
        yaml.safe_dump(cfg, f)

    yield

    with logging_config_path.open('w') as f:
        yaml.safe_dump(old_cfg)
