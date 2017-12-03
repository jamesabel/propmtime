
import shutil
import pytest

import test_propmtime

from propmtime import init_logger, __application_name__, __author__

log = init_logger(__application_name__, __author__, 'temp', True)


@pytest.fixture(scope="session")
def pytest_runtest_setup():
    try:
        shutil.rmtree(test_propmtime.data_root)
    except FileNotFoundError:
        pass
