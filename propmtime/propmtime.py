
# propagate the modification time of a folder/directory from its children (files or folders/directories)

# discussion:
# Many OSs (including Windows) only change the modification time of a folder/directory based on its
# immediate children.  This code analyzes a folder and its children, propagating (changing) the
# modification times of each folder to be the most recent time of all of its children

import os
import time
import propmtime.util
import win32con
from datetime import datetime, timedelta
import inspect
from propmtime.file_mtime import get_mtime_from_file_name


class Propmtime():
    def __init__(self, root, do_update, silent, process_hidden=False, process_system=False, verbose=False):
        self.root = root
        self.do_update = do_update
        self.process_hidden = process_hidden
        self.process_system = process_system
        self.silent = silent
        self.verbose = verbose
        self.total_time = None
        self.error_count = None
        self.files_folders_count = None

    def run(self):
        self.error_count = 0
        self.files_folders_count = 0
        start_time = time.time()

        for walk_path, dirs, files in os.walk(self.root, topdown=False):
            if walk_path is not None:
                latest_time = 0 # empty folders get an mtime of the epoch
                for fs_obj in dirs + files:
                    long_full_path = propmtime.util.get_long_abs_path(os.path.join(walk_path, fs_obj))

                    # decide if we're going to process this file
                    # if were processing all files, avoid the call to get the attributes
                    process_the_file = self.process_hidden and self.process_system
                    if not process_the_file:
                        file_attrib = propmtime.util.get_file_attributes(long_full_path, self.verbose)
                        process_the_file = not file_attrib or \
                                           (self.process_hidden and win32con.FILE_ATTRIBUTE_HIDDEN in file_attrib) or\
                                           (self.process_system and win32con.FILE_ATTRIBUTE_SYSTEM in file_attrib)

                    if process_the_file:
                        self.files_folders_count += 1

                        mtime = None
                        try:
                            mtime = os.path.getmtime(long_full_path)
                        except WindowsError as e:
                            if self.verbose:
                                print(e)
                            self.error_count += 1
                        if mtime and mtime > start_time:
                            # Sometimes mtime can be in the future (and thus invalid).
                            # Try to use the ctime if it is.
                            try:
                                mtime = os.path.getctime(long_full_path)
                            except WindowsError as e:
                                if self.verbose:
                                    print(e)
                                self.error_count += 1
                        if mtime and mtime > start_time:
                            # still in the future - ignore it
                            mtime = None

                        if mtime:
                            # determine if the mtime is different than what's encoded in the file name
                            file_name_mtime = get_mtime_from_file_name(long_full_path)
                            if file_name_mtime is not None:
                                try:
                                    ts = file_name_mtime.timestamp()
                                except OverflowError as e:
                                    print(e, long_full_path)
                                    ts = None
                                    mtime = None
                                if ts is not None:
                                    # use a fairly wide window to allow for passing through time zones
                                    window = 1  # days
                                    if abs(mtime - ts) > timedelta(days=window).total_seconds():
                                        if not self.silent:
                                            print('mtime missmatch: %s (os:%s, filename:%s)' % (long_full_path,
                                                  str(datetime.fromtimestamp(mtime)), str(file_name_mtime)))
                                        if self.do_update:
                                            # adjust the mtime if it's off
                                            if self.verbose:
                                                print('updating mtime to %s' % file_name_mtime.strftime('%c'))
                                            os.utime(long_full_path, (ts, ts))
                                            mtime = ts

                            # make sure it's still not in the future ... if it is, ignore it
                            if mtime is not None and mtime <= start_time:
                                latest_time = max(mtime, latest_time)

                long_path = propmtime.util.get_long_abs_path(walk_path)
                try:
                    try:
                        mtime = os.path.getmtime(long_path)
                        # don't change it if it's close (there can be rounding errors, etc.)
                        if abs(latest_time - mtime) > 2:
                            os.utime(long_path, (latest_time, latest_time))
                    except WindowsError as e:
                        if self.verbose:
                            print(e)
                        self.error_count += 1
                except UnicodeEncodeError as e2:
                    print(e2)

        self.total_time = time.time() - start_time

    def print_stats(self):
        if self.error_count > 0:
            print((self.error_count, "total errors"))
        print("total files/folders/directories : %s" % self.files_folders_count)
        print("elapsed time : %s" % self.total_time, "sec")

