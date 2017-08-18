
import argparse
import os
import time
import threading

import propmtime.util
import propmtime.logger

if propmtime.util.is_windows():
    import win32con

# PEP 440 compliant
# adhere to http://semver.org/
__version__ = '0.0.2'

# required for OSNAP
__author__ = 'abel.co'
__application_name__ = 'propmtime'
__python_version__ = '3.6.0'

__url__ = 'https://github.com/jamesabel/propmtime'


def _process_the_file(process_hidden, process_system, path):
    if process_hidden and process_system:
        # we're processing everything so just return True
        return True
    is_hidden, is_system = propmtime.util.get_file_attributes(path)
    return (not (is_hidden or is_system)) or (is_hidden and process_hidden) or (is_system and process_system)


def _do_propagation(containing_folder, fs_objs, current_time, update, process_hidden, process_system):
    """
    propagate the mtime of one folder
    :param containing_folder: parent folder
    :param fs_objs: file system objects (files and folders) to be used to determine the most recent mtime (i.e. the children of parent folder)
    :param current_time: current time in seconds from epoch
    :return: file_folders_count, error_count
    """
    latest_time = 0  # empty folders get an mtime of the epoch
    files_folders_count = 0
    error_count = 0
    for fs_obj in fs_objs:
        long_full_path = propmtime.util.get_long_abs_path(os.path.join(containing_folder, fs_obj))
        if _process_the_file(process_hidden, process_system, long_full_path):
            files_folders_count += 1
            mtime = None
            try:
                mtime = os.path.getmtime(long_full_path)
            except OSError as e:
                propmtime.logger.log.warn(e)
                error_count += 1
            if mtime and mtime > current_time:
                # Sometimes mtime can be in the future (and thus invalid).
                # Try to use the ctime if it is.
                try:
                    mtime = os.path.getctime(long_full_path)
                except OSError as e:
                    propmtime.logger.log.warn(e)
                    error_count += 1
            if mtime and mtime > current_time:
                # still in the future - ignore it
                mtime = None
            if mtime:
                # make sure it's still not in the future ... if it is, ignore it
                if mtime <= current_time:
                    latest_time = max(mtime, latest_time)

    long_path = propmtime.util.get_long_abs_path(containing_folder)
    try:
        mtime = os.path.getmtime(long_path)
        # don't change it if it's close (there can be rounding errors, etc.)
        if abs(latest_time - mtime) > 2 and update:
            propmtime.logger.log.info('updating %s to %s' % (long_path, mtime))
            os.utime(long_path, (latest_time, latest_time))
    except OSError as e:
        # these are things like access denied and we don't want to see that under normal operation
        propmtime.logger.log.debug(e)
        error_count += 1
    except UnicodeEncodeError as e:
        propmtime.logger.log.error(e)
        error_count += 1
    return files_folders_count, error_count


def event(root, event_file_path, update, process_hidden, process_system):
    propmtime.logger.log.info('event : %s , %s' % (root, event_file_path))
    if _process_the_file(process_hidden, process_system, event_file_path):
        propmtime.logger.log.info('processing : %s' % event_file_path)
        current_time = time.time()
        current_folder = os.path.dirname(event_file_path)
        while os.path.abspath(current_folder) != os.path.abspath(root):
            if len(current_folder) < len(root):
                raise RuntimeError
            fs_objs = os.listdir(current_folder)
            _do_propagation(current_folder, fs_objs, current_time, update, process_hidden, process_system)
            current_folder = os.path.dirname(current_folder)
    else:
        propmtime.logger.log.info('not processed : %s' % event_file_path)


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

        propmtime.logger.log.info('scan started : %s' % self._root)
        propmtime.logger.log.info('process_hidden : %s' % self._process_hidden)
        propmtime.logger.log.info('process_system : %s' % self._process_system)
        propmtime.logger.log.info('update : %s' % self._update)

        for walk_folder, dirs, files in os.walk(self._root, topdown=False):
            if self._request_exit_flag:
                break
            if walk_folder:
                # For Mac we have to explicitly check to see if this path is hidden.
                # For Windows this is taken care of with the hidden file attribute.
                if (propmtime.util.is_mac() and (self._process_hidden or '/.' not in walk_folder))\
                        or not propmtime.util.is_mac():
                    ffc, ec = _do_propagation(walk_folder, dirs + files, start_time, self._update, self._process_hidden, self._process_system)
                    files_folders_count += ffc
                    error_count += ec
                else:
                    propmtime.logger.log.debug('skipping %s' % walk_folder)
            else:
                propmtime.logger.log.warn('no os.walk root')

        total_time = time.time() - start_time

        propmtime.logger.log.info('scan complete : %s (%f seconds)' % (self._root, time.time() - start_time))
        propmtime.logger.log.info('file_folders_count : %s' % files_folders_count)
        propmtime.logger.log.info('error_count : %s' % error_count)
        propmtime.logger.log.info('total_time : %s' % total_time)

        return files_folders_count, error_count, total_time

    def request_exit(self):
        self._request_exit_flag = True


def main():
    propmtime.logger.init()
    desc = """Many OSs (including Windows) only change the modification time of a folder/directory based on its immediate children.
    This code analyzes a folder and all of its children, and propagates (changes) the modification times of each folder to
    be the most recent time of all of its children."""
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-n', '--noupdate', action='store_true', default=False, help='Supress updating the mtime')
    parser.add_argument("-p", "--path", default=".", help='Path to folder or directory.  (default=".")')
    parser.add_argument('--hidden', action='store_true', default=False)
    parser.add_argument('--system', action='store_true', default=False)
    args = parser.parse_args()
    if args.verbose:
        propmtime.util.set_verbose_logging()
    pmt = PropMTime(args.path, not args.noupdate, args.hidden, args.system)
    pmt.start()
    # todo: look for keypress to signal an exit
    pmt.join()

if __name__ == "__main__":
    main()
