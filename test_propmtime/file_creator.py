import os
import propmtime

from test_propmtime import time_offset_unit

if propmtime.os_util.is_windows():
    import win32api
    import win32con


def file_creator(current_time, file_path, time_offset, is_hidden, is_system):
    folder = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    os.makedirs(folder, exist_ok=True)
    if propmtime.os_util.is_mac() and is_hidden:
        assert(file_name[0] == '.')
    full_path = os.path.join(folder, file_name)
    if propmtime.os_util.is_windows() and os.path.exists(full_path):
        win32api.SetFileAttributes(full_path, win32con.FILE_ATTRIBUTE_NORMAL)
    with open(full_path, "w") as f:
        f.write(os.path.abspath(full_path))  # just put something in the file ... this is as good as anything
    if propmtime.os_util.is_windows():
        if is_hidden:
            win32api.SetFileAttributes(full_path, win32con.FILE_ATTRIBUTE_HIDDEN)
        if is_system:
            win32api.SetFileAttributes(full_path, win32con.FILE_ATTRIBUTE_SYSTEM)
    mtime = current_time - (time_offset * time_offset_unit)  # set file's mtime back in time
    os.utime(full_path, (mtime, mtime))
    return mtime
