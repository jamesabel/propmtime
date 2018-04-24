
import shutil
import pytest

from balsa import get_logger, Balsa

import test_propmtime

from propmtime import __application_name__, __author__

log = get_logger(__file__)


@pytest.fixture(scope="session")
def pytest_runtest_setup():
    balsa = Balsa(__application_name__, __author__)
    balsa.init_logger()
    try:
        shutil.rmtree(test_propmtime.data_root)
    except FileNotFoundError:
        pass
