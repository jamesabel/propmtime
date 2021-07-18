import os
from pathlib import Path
import time
from datetime import timedelta
import math

from balsa import get_logger
from typeguard import typechecked

import propmtime
import propmtime.os_util
import test_propmtime
from propmtime import mkdirs

if propmtime.os_util.is_windows():
    import win32api
    import win32con

log = get_logger("test_propmtime")

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


@typechecked(always=True)
def file_creator(file_path: Path, is_hidden: bool, is_system: bool, init: bool):
    folder = file_path.parent
    file_name = file_path.name
    if init:
        mkdirs(folder, remove_first=True)
    if propmtime.os_util.is_mac() and is_hidden:
        assert file_name[0] == "."
    full_path = Path(folder, file_name)
    full_path.write_text(str(full_path.absolute()))  # just put something in the file ... this is as good as anything
    if propmtime.os_util.is_windows():
        if is_hidden:
            win32api.SetFileAttributes(str(full_path), win32con.FILE_ATTRIBUTE_HIDDEN)
        if is_system:
            win32api.SetFileAttributes(str(full_path), win32con.FILE_ATTRIBUTE_SYSTEM)
    mtime = file_mtimes[is_hidden, is_system]
    os.utime(str(full_path), (mtime, mtime))
    return mtime


@typechecked(always=True)
def check_mtimes(parent_dir: Path, file_path: Path, is_hidden: bool, is_system: bool):
    parent_mtime = os.path.getmtime(str(parent_dir))
    file_mtime = os.path.getmtime(str(file_path))
    log.info(f"{parent_dir=} {parent_mtime=}")
    log.info(f"{file_path=} {file_mtime}")
    expected_parent_mtime = expected_file_mtimes[is_hidden, is_system]
    ok = math.isclose(parent_mtime, expected_parent_mtime, abs_tol=2.0)
    if not ok:
        time_difference = abs(parent_mtime - expected_parent_mtime)
        log.warning(f"{parent_dir=} {file_path=} {parent_mtime=} {expected_parent_mtime=} {time_difference=}")
    assert ok


def run(is_hidden: bool, is_system: bool, process_dot_folders_as_normal: bool):
    file_name = "myfile.txt"
    if propmtime.os_util.is_mac() and is_hidden:
        file_name = "." + file_name
    file_path = Path(test_propmtime.child_folder, file_name)
    file_creator(file_path, False, False, True)

    # put in system and hidden files at later times
    system_file_path = Path(test_propmtime.child_folder, "my_system_file.txt")
    file_creator(system_file_path, False, True, False)
    hidden_file_path = Path(test_propmtime.child_folder, "my_hidden_file.txt")
    file_creator(hidden_file_path, True, False, False)
    both_file_path = Path(test_propmtime.child_folder, "my_hidden_system_file.txt")
    file_creator(both_file_path, True, True, False)

    # make sure the file mtimes are correct
    assert math.isclose(os.path.getmtime(hidden_file_path), hidden_mtime, abs_tol=2.0)
    assert math.isclose(os.path.getmtime(system_file_path), system_mtime, abs_tol=2.0)
    assert math.isclose(os.path.getmtime(both_file_path), both_mtime, abs_tol=2.0)

    pmt = propmtime.PropMTime(test_propmtime.data_parent, True, is_hidden, is_system, process_dot_folders_as_normal, lambda x: x)
    pmt.start()
    pmt.join()

    check_mtimes(test_propmtime.data_parent, file_path, is_hidden, is_system)

    # make sure the original files times have not changed
    assert math.isclose(os.path.getmtime(hidden_file_path), hidden_mtime, abs_tol=2.0)
    assert math.isclose(os.path.getmtime(system_file_path), system_mtime, abs_tol=2.0)
    assert math.isclose(os.path.getmtime(both_file_path), both_mtime, abs_tol=2.0)


def test_normal():
    run(False, False, False)


def test_hidden():
    run(True, False, False)


def test_system():
    run(False, True, False)


def test_both():
    run(True, True, False)
