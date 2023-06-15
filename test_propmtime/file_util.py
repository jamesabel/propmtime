import math
import os
from pathlib import Path
import zipfile

import win32api
import win32con
from typeguard import typechecked
from balsa import get_logger


from propmtime import is_mac, is_windows, set_mtime
from test_propmtime import application_name, ABS_TOLERANCE

log = get_logger(application_name)

data_root = Path(application_name, "data")


@typechecked()
def file_creator(file_path: Path, mtime: float, is_hidden: bool = False, is_system: bool = False):
    """
    create a test file
    :param file_path: file path
    :param mtime: file mtime
    :param is_hidden: True if OS "Hidden"
    :param is_system: True if OS "System"
    :param init: True to remove the parent directory entirely before write
    :return: mtime of created file
    """
    if is_mac() and is_hidden:
        assert file_path.name[0] == "."
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists() and is_windows():
        win32api.SetFileAttributes(str(file_path), win32con.FILE_ATTRIBUTE_NORMAL)  # so we can write existing files, even if they're system or hidden
    file_path.write_text(str(file_path.absolute()))  # just put something in the file ... this is as good as anything
    if is_windows():
        if is_hidden:
            win32api.SetFileAttributes(str(file_path), win32con.FILE_ATTRIBUTE_HIDDEN)
        if is_system:
            win32api.SetFileAttributes(str(file_path), win32con.FILE_ATTRIBUTE_SYSTEM)
    set_mtime(file_path, mtime, True)
    return mtime


@typechecked()
def check_mtime(file_path: Path, expected_mtime: float):
    actual_mtime = os.path.getmtime(str(file_path))
    log.info(f"{file_path=} {actual_mtime}")
    ok = math.isclose(actual_mtime, expected_mtime, abs_tol=ABS_TOLERANCE)
    if not ok:
        time_difference = abs(actual_mtime - expected_mtime)
        log.error(f"{file_path=} {actual_mtime=} {expected_mtime=} {time_difference=}")
    assert ok


@typechecked()
def create_zip(folder_path: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(folder_path))
