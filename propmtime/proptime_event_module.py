import os
from pathlib import Path
import time

from balsa import get_logger

from propmtime import __application_name__, get_file_attributes, get_long_abs_path

log = get_logger(__application_name__)


def _process_file_test(process_hidden: bool, process_system: bool, path: Path):
    if process_hidden and process_system:
        # we're processing everything so just return True
        return True
    is_hidden, is_system = get_file_attributes(path)
    return (not (is_hidden or is_system)) or (is_hidden and process_hidden) or (is_system and process_system)


def do_propagation(containing_folder, fs_objs, current_time, update: bool, process_hidden: bool, process_system: bool, process_dot_as_normal: bool, set_blinking):
    """
    propagate the mtime of one folder
    :param containing_folder: parent folder
    :param fs_objs: file system objects (files and folders) to be used to determine the most recent mtime (i.e. the children of parent folder)
    :param current_time: current time in seconds from epoch
    :return: file_folders_count, error_count
    """
    error_count = 0
    files_folders_count = 0
    containing_folder_path = Path(containing_folder)
    if containing_folder_path.is_dir():
        set_blinking(True)
        latest_time = 0  # empty folders get an mtime of the epoch
        for fs_obj in fs_objs:
            long_full_path = get_long_abs_path(os.path.join(containing_folder, fs_obj))
            if not process_dot_as_normal and len(long_full_path.name) > 0 and long_full_path.name[0] == ".":
                log.debug(f"skipping dot file/folder {long_full_path=}")
            elif _process_file_test(process_hidden, process_system, long_full_path):
                files_folders_count += 1
                mtime = None
                try:
                    mtime = os.path.getmtime(long_full_path)
                except OSError as e:
                    log.info(e)  # quite possible to get an access error
                    error_count += 1
                if mtime and mtime > current_time:
                    # Sometimes mtime can be in the future (and thus invalid).
                    # Try to use the ctime if it is.
                    try:
                        mtime = os.path.getctime(long_full_path)
                    except OSError as e:
                        log.warn(e)
                        error_count += 1
                if mtime and mtime > current_time:
                    # still in the future - ignore it
                    mtime = None
                if mtime:
                    # make sure it's still not in the future ... if it is, ignore it
                    if mtime <= current_time:
                        latest_time = max(mtime, latest_time)

        containing_folder_long_path = get_long_abs_path(containing_folder)
        try:
            mtime = os.path.getmtime(containing_folder_long_path)
            # don't change it if it's close (there can be rounding errors, etc.)
            if abs(latest_time - mtime) > 2 and update:
                log.debug("updating %s to %s" % (containing_folder_long_path, mtime))
                os.utime(containing_folder_long_path, (latest_time, latest_time))
        except OSError as e:
            # these are things like access denied and we don't want to see that under normal operation
            log.debug(e)
            error_count += 1
        except UnicodeEncodeError as e:
            log.error(e)
            error_count += 1
        set_blinking(False)

    else:
        log.error(f"{containing_folder_path=} is not a directory")
        error_count += 1
    return files_folders_count, error_count


def propmtime_event(root, event_file_path, update, process_hidden: bool, process_system: bool, process_dot_as_normal: bool, set_blinking):
    """
    propmtime upon a watchdog event
    :param self:
    :param root:
    :param event_file_path:
    :param update:
    :param process_hidden:
    :param process_system:
    :return:
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
                do_propagation(current_folder, fs_objs, current_time, update, process_hidden, process_system, process_dot_as_normal, set_blinking)
                current_folder = os.path.dirname(current_folder)
            except FileNotFoundError as e:
                log.info(str(e))
    else:
        log.info("not processed : %s" % event_file_path)
