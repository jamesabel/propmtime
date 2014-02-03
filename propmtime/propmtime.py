
# propagate the modification time of a folder/directory from its children (files or folders/directories)

# discussion:
# Many OSs (including Windows) only change the modification time of a folder/directory based on its
# immediate children.  This code analyzes a folder and its children, propagating (changing) the
# modification times of each folder to be the most recent time of all of its children

import os
import time
import propmtime.util
import win32con

class Propmtime():
    def __init__(self, root, process_hidden = False, process_system = False, print_flag = False):
        self.root = root
        self.process_hidden = process_hidden
        self.process_system = process_system
        self.print_flag = print_flag

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
                    process_the_file = self.process_hidden and self.process_system # if were processing all files, avoid the call to get the attributes
                    if not process_the_file:
                        file_attrib = propmtime.util.get_file_attributes(long_full_path)
                        process_the_file = not file_attrib or \
                                           (self.process_hidden and win32con.FILE_ATTRIBUTE_HIDDEN in file_attrib) or\
                                           (self.process_system and win32con.FILE_ATTRIBUTE_SYSTEM in file_attrib)

                    if process_the_file:
                        self.files_folders_count += 1
                        try:
                            mtime = os.path.getmtime(long_full_path)
                            if mtime > start_time:
                                # Sometimes mtime can be in the future (and thus invalid).
                                # Try to use the ctime if it is.
                                mtime = os.path.getctime(long_full_path)
                        except WindowsError:
                            if self.print_flag:
                                print('WindowsError', long_full_path)
                            self.error_count += 1
                        # make sure it's still not in the future ... if it is, ignore it
                        if mtime <= start_time:
                            latest_time = max(mtime, latest_time)

                long_path = propmtime.util.get_long_abs_path(walk_path)
                try:
                    mtime = os.path.getmtime(long_path)
                    # don't change it if it's close (there can be rounding errors, etc.)
                    if abs(latest_time - mtime) > 2:
                        os.utime(long_path, (latest_time, latest_time))
                except WindowsError:
                    if self.print_flag:
                        print('WindowsError', long_path)
                    self.error_count += 1

        self.total_time = time.time() - start_time

    def print_stats(self):
        if self.error_count > 0:
            print((self.error_count, "total errors"))
        print(("total files/folders/directories:", self.files_folders_count))
        print(("elapsed time:", self.total_time, "sec"))

