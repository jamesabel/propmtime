import os
import operator
from pathlib import Path

from balsa import get_logger
from typeguard import typechecked

import propmtime
import propmtime.os_util
import test_propmtime

log = get_logger("test_propmtime")


@typechecked(always=True)
def check_mtimes(parent_dir: Path, file_path: Path, operator_method):

    parent_mtime = os.path.getmtime(str(parent_dir))
    file_mtime = os.path.getmtime(str(file_path))
    log.info(f"{parent_dir=} {parent_mtime=}")
    log.info(f"{file_path=} {file_mtime}")
    mtime_difference = abs(parent_mtime - file_mtime)
    log.info(f"{mtime_difference=}")
    middle_of_time_window = test_propmtime.time_offset_sec/2.0
    ok = operator_method(mtime_difference, middle_of_time_window)
    if not ok:
        log.warning(f"{parent_dir=} {file_path=} {mtime_difference=}")
    assert ok


def run(is_hidden: bool, is_system: bool):

    file_name = "myfile.txt"
    if propmtime.os_util.is_mac() and is_hidden:
        file_name = "." + file_name
    file_path = Path(test_propmtime.child_folder, file_name)
    test_propmtime.file_creator(file_path, test_propmtime.time_offset_sec, is_hidden, is_system)

    check_mtimes(test_propmtime.data_parent, file_path, operator.gt)

    pmt = propmtime.PropMTime(test_propmtime.data_parent, True, is_hidden, is_system)
    pmt.start()
    pmt.join()

    check_mtimes(test_propmtime.data_parent, file_path, operator.lt)


def test_normal():
    run(False, False)


def test_hidden():
    run(True, False)


def test_system():
    run(False, True)


def test_both():
    run(True, True)
