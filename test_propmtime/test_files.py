import os
from pathlib import Path
import math
import time
from datetime import timedelta

from balsa import get_logger

from propmtime import is_mac, PropMTime
from test_propmtime import file_creator, check_mtime, mkdirs, ABS_TOLERANCE, data_root

test_name = "test_files"

data_parent = Path(data_root, test_name, "parent")
data_child = Path(data_parent, "child")

log = get_logger(test_name)

regular_mtime = time.time() - timedelta(minutes=10).total_seconds()
hidden_mtime = regular_mtime + timedelta(minutes=2).total_seconds()
system_mtime = regular_mtime + timedelta(minutes=4).total_seconds()
both_mtime = regular_mtime + timedelta(minutes=6).total_seconds()

# fmt: off

# (is_hidden, is_system)
file_mtimes = {(False, False): regular_mtime,
               (False, True): system_mtime,
               (True, False): hidden_mtime,
               (True, True): both_mtime}

# (is_hidden, is_system)
expected_file_mtimes = {(False, False): regular_mtime,
                        (False, True): both_mtime,
                        (True, False): hidden_mtime,
                        (True, True): both_mtime  # both mtime is later than the system-only
                        }

# fmt: on


def tst_files(is_hidden: bool, is_system: bool, process_dot_folders_as_normal: bool):
    mkdirs(data_child)

    file_name = "my_normal_file.txt"
    if is_mac() and is_hidden:
        file_name = "." + file_name
    normal_file_path = Path(data_child, file_name)
    file_creator(normal_file_path, file_mtimes[False, False])

    # put in system and hidden files at later times
    system_file_path = Path(data_child, "my_system_file.txt")
    file_creator(system_file_path, file_mtimes[False, True], is_system=True)
    hidden_file_path = Path(data_child, "my_hidden_file.txt")
    file_creator(hidden_file_path, file_mtimes[True, False], is_hidden=True)
    both_file_path = Path(data_child, "my_hidden_system_file.txt")
    file_creator(both_file_path, file_mtimes[True, True], True, True)

    # make sure the initial file mtimes are correct
    assert math.isclose(os.path.getmtime(hidden_file_path), hidden_mtime, abs_tol=ABS_TOLERANCE)
    assert math.isclose(os.path.getmtime(system_file_path), system_mtime, abs_tol=ABS_TOLERANCE)
    assert math.isclose(os.path.getmtime(both_file_path), both_mtime, abs_tol=ABS_TOLERANCE)

    pmt = PropMTime(data_parent, True, is_hidden, is_system, process_dot_folders_as_normal, print)
    pmt.start()
    pmt.join()

    check_mtime(data_parent, expected_file_mtimes[is_hidden, is_system])

    # make sure the original files times have not changed
    assert math.isclose(os.path.getmtime(hidden_file_path), hidden_mtime, abs_tol=ABS_TOLERANCE)
    assert math.isclose(os.path.getmtime(system_file_path), system_mtime, abs_tol=ABS_TOLERANCE)
    assert math.isclose(os.path.getmtime(both_file_path), both_mtime, abs_tol=ABS_TOLERANCE)


def test_normal():
    tst_files(False, False, False)


def test_hidden():
    tst_files(True, False, False)


def test_system():
    tst_files(False, True, False)


def test_both():
    tst_files(True, True, False)
