
import shutil
import pytest
import logging

import propmtime.util
import propmtime.logger
import test_propmtime

@pytest.fixture(scope="session")
def pytest_runtest_setup():
    if propmtime.logger.log is None:
        # todo: the session scope doesn't work - this is a workaround so we only init log once
        propmtime.logger.init()
        propmtime.logger.set_console_log_level(logging.INFO)
    try:
        shutil.rmtree(test_propmtime.data_root)
    except FileNotFoundError:
        pass

