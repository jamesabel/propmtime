from pathlib import Path
import pytest

from balsa import get_logger, Balsa

import test_propmtime

from propmtime import __application_name__, __author__, rmdir

log = get_logger(__file__)


@pytest.fixture(scope="session", autouse=True)
def tst_setup():
    balsa = Balsa(__application_name__, __author__, log_directory="log", delete_existing_log_files=True)
    balsa.init_logger()
    rmdir(Path(test_propmtime.data_parent))
