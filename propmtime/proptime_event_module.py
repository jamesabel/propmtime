import os
from pathlib import Path
import time
from typing import Callable, List
import threading
import zipfile
from datetime import datetime

from balsa import get_logger
from typeguard import typechecked

from propmtime import __application_name__, get_file_attributes, get_long_abs_path, is_mac, is_exit_requested


log = get_logger(__application_name__)


@typechecked()
def _process_file_test(process_hidden: bool, process_system: bool, path: Path):
    if process_hidden and process_system:
        # we're processing everything so just return True
        return True
    is_hidden, is_system = get_file_attributes(path)
    return (not (is_hidden or is_system)) or (is_hidden and process_hidden) or (is_system and process_system)


@typechecked()
def zip_info_to_mtime(file_object: zipfile.ZipInfo, zip_path: Path) -> float:
    dt = file_object.date_time
    try:
        mtime_datetime = datetime(year=dt[0], month=dt[1], day=dt[2], hour=dt[3], minute=dt[4], second=dt[5])
        mtime = mtime_datetime.timestamp()
    except ValueError as e:
        # We have seen zip files with internal files that have no mtime. Handle that as gracefully as possible.
        # e.g.: dt=(2019, 11, 0, 23, 54, 6),day is out of range for month
        log.info(f'filename="{file_object.filename}",{zip_path=},{dt=},{e}')
        mtime = 0.0  # so this file won't be selected as the most recent
    return mtime


@typechecked()
def set_mtime(path: Path, new_mtime: float, update: bool) -> int:
    """
    set the file or folder's mtime
    :param path:
    :param new_mtime:
    :param update:
    :return:
    """
    error_count = 0
    try:
        existing_mtime = os.path.getmtime(path)
        # don't change it if it's close (there can be rounding errors, etc.)
        if abs(new_mtime - existing_mtime) > 2 and update:
            log.debug(f'updating "{path}" to {new_mtime}')
            os.utime(path, (new_mtime, new_mtime))
    except OSError as e:
        # these are things like access denied, and we don't want to see that under normal operation
        log.debug(e)
        error_count = 1
    except UnicodeEncodeError as e:
        log.error(e)
        error_count = 1
    return error_count


@typechecked()
def _do_propagation(
    containing_folder: Path, fs_objs: List, current_time: float, update: bool, process_hidden: bool, process_system: bool, process_dot_as_normal: bool, running_callback: Callable
):
    """
    propagate the mtime of one folder
    :param containing_folder: parent folder
    :param fs_objs: file system objects (files and folders) to be used to determine the most recent mtime (i.e. the children of parent folder)
    :param current_time: current time in seconds from epoch
    :param update: True to update the mtime (False to do a "dry run")
    :param process_hidden: process "Hidden" files (from the OS perspective)
    :param process_system: process "System" files (from the OS perspective)
    :param process_dot_as_normal: process "dot" files as normal files (not System file)
    :return: file_folders_count, error_count
    """
    error_count = 0
    files_folders_count = 0
    containing_folder_path = Path(containing_folder)
    if containing_folder_path.is_dir():
        latest_time = 0.0  # empty folders get an mtime of the epoch
        for fs_obj in fs_objs:
            long_full_path = get_long_abs_path(Path(containing_folder, fs_obj))
            running_callback(str(long_full_path))
            if not process_dot_as_normal and len(long_full_path.name) > 0 and long_full_path.name[0] == ".":
                log.debug(f"skipping dot file/folder {long_full_path=}")
            elif _process_file_test(process_hidden, process_system, long_full_path):
                mtime = None  # if a file has a .zip extension but isn't really a zip, treat it as a regular file below

                if long_full_path.name.lower().endswith(".zip"):
                    # count files in a zip as if they exist unzipped
                    try:
                        with zipfile.ZipFile(long_full_path) as zip_file:
                            for file_object in zip_file.infolist():
                                file_mtime = zip_info_to_mtime(file_object, long_full_path)
                                if mtime is None or file_mtime > mtime:
                                    mtime = file_mtime
                                    files_folders_count += 1
                    except (zipfile.BadZipFile, OSError) as e:
                        log.info(f'"{long_full_path}",{e}')
                        error_count += 1
                    if mtime is not None:
                        error_count += set_mtime(long_full_path, mtime, update)  # set mtime of zip file itself

                if mtime is None:
                    files_folders_count += 1
                    mtime = None
                    try:
                        mtime = os.path.getmtime(long_full_path)
                    except OSError as e:
                        log.info(e)  # possible to get an "access error"
                        error_count += 1

                if mtime is not None and mtime > current_time:
                    # Sometimes mtime can be in the future (and thus invalid).
                    # Try to use the ctime if it is.
                    try:
                        mtime = os.path.getctime(long_full_path)
                    except OSError as e:
                        log.warn(e)
                        error_count += 1

                # if still in the future ignore it
                if mtime is not None and mtime <= current_time:
                    latest_time = max(mtime, latest_time)

        containing_folder_long_path = get_long_abs_path(containing_folder)
        error_count += set_mtime(containing_folder_long_path, latest_time, update)

    else:
        log.error(f"{containing_folder_path=} is not a directory")
        error_count += 1

    return files_folders_count, error_count


@typechecked()
def propmtime_event(root, event_file_path, update, process_hidden: bool, process_system: bool, process_dot_as_normal: bool, running_callback: Callable):
    """
    propmtime upon a watchdog event

    :param root: root folder to observe
    :param event_file_path: event path
    :param update: True to do the update (False for dry run)
    :param process_hidden: True to process Hidden files
    :param process_system: True to process System files
    :param process_dot_as_normal: True to process "dot" files as normal files (False to process them as System files)
    :param running_callback: will be called when propagation is running
    """
    log.info("event : %s , %s" % (root, event_file_path))
    if _process_file_test(process_hidden, process_system, event_file_path):
        log.info("processing : %s" % event_file_path)
        current_time = time.time()
        current_folder = os.path.dirname(event_file_path)
        while os.path.abspath(current_folder) != os.path.abspath(root):
            if len(current_folder) < len(root):
                raise RuntimeError
            try:
                fs_objs = os.listdir(current_folder)
                _do_propagation(current_folder, fs_objs, current_time, update, process_hidden, process_system, process_dot_as_normal, running_callback)
                current_folder = os.path.dirname(current_folder)
            except FileNotFoundError as e:
                log.info(str(e))
    else:
        log.info("not processed : %s" % event_file_path)


class PropMTime(threading.Thread):
    @typechecked()
    def __init__(self, root, update: bool, process_hidden: bool, process_system: bool, process_dot_as_normal: bool, running_callback: Callable):
        self._root = root
        self._update = update
        self._process_hidden = process_hidden
        self._process_system = process_system
        self._process_dot_as_normal = process_dot_as_normal
        self._running_callback = running_callback
        self.error_count = 0
        self.files_folders_count = 0
        self.total_time = None
        super().__init__()

    # scan and propagate the modification time of a folder/directory from its children (files or folders/directories)
    def run(self):
        start_time = time.time()

        log.debug(f"{self._root} : scan started")
        log.debug(f"{self._root} : {self._process_hidden=}")
        log.debug(f"{self._root} : {self._process_system=}")
        log.debug(f"{self._root} : {self._process_system=}")
        log.debug(f"{self._root} : {self._update=}")

        for walk_folder, dirs, files in os.walk(self._root, topdown=False):
            if is_exit_requested():
                break
            if walk_folder:
                # For Mac we have to explicitly check to see if this path is hidden.
                # For Windows this is taken care of with the hidden file attribute.
                if (is_mac() and (self._process_hidden or "/." not in walk_folder)) or not is_mac():
                    ffc, ec = _do_propagation(
                        Path(walk_folder), dirs + files, start_time, self._update, self._process_hidden, self._process_system, self._process_dot_as_normal, self._running_callback
                    )
                    self.files_folders_count += ffc
                    self.error_count += ec
                else:
                    log.debug("skipping %s" % walk_folder)
            else:
                log.warn("no os.walk root")

        self.total_time = time.time() - start_time

        log.info(f"{self._root} : is_exit_requested : {is_exit_requested()}")
        log.info(f"{self._root} : file_folders_count : {self.files_folders_count}")
        log.info(f"{self._root} : error_count : {self.error_count}")
        log.info(f"{self._root} : total_time : {self.total_time} seconds")

        self._running_callback("")  # normal icon
