
import os
import threading
import time

import pressenter2exit

from propmtime import get_logger, init_logger, __application_name__, __author__, is_windows, is_mac, get_file_attributes
from propmtime import get_long_abs_path, get_arguments
from propmtime import set_blinking

if is_windows():
    import win32con

log = get_logger(__application_name__)


def init_propmtime_logger(args):
    return init_logger(__application_name__, __author__, args.logdir, args.verbose, args.dellog)


def _process_the_file(process_hidden, process_system, path):
    if process_hidden and process_system:
        # we're processing everything so just return True
        return True
    is_hidden, is_system = get_file_attributes(path)
    return (not (is_hidden or is_system)) or (is_hidden and process_hidden) or (is_system and process_system)


def do_propagation(containing_folder, fs_objs, current_time, update, process_hidden, process_system):
    """
    propagate the mtime of one folder
    :param containing_folder: parent folder
    :param fs_objs: file system objects (files and folders) to be used to determine the most recent mtime (i.e. the children of parent folder)
    :param current_time: current time in seconds from epoch
    :return: file_folders_count, error_count
    """
    set_blinking(True)
    latest_time = 0  # empty folders get an mtime of the epoch
    files_folders_count = 0
    error_count = 0
    for fs_obj in fs_objs:
        long_full_path = get_long_abs_path(os.path.join(containing_folder, fs_obj))
        if _process_the_file(process_hidden, process_system, long_full_path):
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

    long_path = get_long_abs_path(containing_folder)
    try:
        mtime = os.path.getmtime(long_path)
        # don't change it if it's close (there can be rounding errors, etc.)
        if abs(latest_time - mtime) > 2 and update:
            log.debug('updating %s to %s' % (long_path, mtime))
            os.utime(long_path, (latest_time, latest_time))
    except OSError as e:
        # these are things like access denied and we don't want to see that under normal operation
        log.debug(e)
        error_count += 1
    except UnicodeEncodeError as e:
        log.error(e)
        error_count += 1
    set_blinking(False)
    return files_folders_count, error_count


def propmtime_event(root, event_file_path, update, process_hidden, process_system):
    log.info('event : %s , %s' % (root, event_file_path))
    if _process_the_file(process_hidden, process_system, event_file_path):
        log.info('processing : %s' % event_file_path)
        current_time = time.time()
        current_folder = os.path.dirname(event_file_path)
        while os.path.abspath(current_folder) != os.path.abspath(root):
            if len(current_folder) < len(root):
                raise RuntimeError
            try:
                fs_objs = os.listdir(current_folder)
                do_propagation(current_folder, fs_objs, current_time, update, process_hidden, process_system)
                current_folder = os.path.dirname(current_folder)
            except FileNotFoundError as e:
                log.info(str(e))
    else:
        log.info('not processed : %s' % event_file_path)


class PropMTime(threading.Thread):
    def __init__(self, root, update, process_hidden, process_system):
        self._root = root
        self._update = update
        self._process_hidden = process_hidden
        self._process_system = process_system
        self._request_exit_flag = False
        super().__init__()

    # scan and propagate the modification time of a folder/directory from its children (files or folders/directories)
    def run(self):
        error_count = 0
        files_folders_count = 0
        start_time = time.time()

        log.info('scan started : %s' % self._root)
        log.info('process_hidden : %s' % self._process_hidden)
        log.info('process_system : %s' % self._process_system)
        log.info('update : %s' % self._update)

        for walk_folder, dirs, files in os.walk(self._root, topdown=False):
            if self._request_exit_flag:
                break
            if walk_folder:
                # For Mac we have to explicitly check to see if this path is hidden.
                # For Windows this is taken care of with the hidden file attribute.
                if (is_mac() and (self._process_hidden or '/.' not in walk_folder)) or not is_mac():
                    ffc, ec = do_propagation(walk_folder, dirs + files, start_time, self._update, self._process_hidden, self._process_system)
                    files_folders_count += ffc
                    error_count += ec
                else:
                    log.debug('skipping %s' % walk_folder)
            else:
                log.warn('no os.walk root')

        total_time = time.time() - start_time

        log.info('scan complete : %s (%f seconds)' % (self._root, time.time() - start_time))
        log.info('file_folders_count : %s' % files_folders_count)
        log.info('error_count : %s' % error_count)
        log.info('total_time : %s' % total_time)

        return files_folders_count, error_count, total_time

    def request_exit(self):
        self._request_exit_flag = True


def cli_main():

    args = get_arguments()
    init_propmtime_logger(args)

    exit_control = pressenter2exit.PressEnter2Exit('%s : enter pressed - will now exit' % __application_name__, None)
    pmt = PropMTime(args.path, not args.noupdate, args.hidden, args.system)
    pmt.start()
    while pmt.is_alive() and exit_control.is_alive():
        time.sleep(0.1)
    if pmt.is_alive():
        pmt.request_exit()
    pmt.join()


if __name__ == "__main__":
    cli_main()
