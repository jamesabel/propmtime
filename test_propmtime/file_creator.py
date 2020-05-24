import os
import propmtime
from pathlib import Path
import time

from typeguard import typechecked
from propmtime import mkdirs

if propmtime.os_util.is_windows():
    import win32api
    import win32con


@typechecked(always=True)
def file_creator(file_path: Path, time_offset: float, is_hidden: bool, is_system: bool):
    folder = file_path.parent
    file_name = file_path.name
    mkdirs(folder, remove_first=True)
    if propmtime.os_util.is_mac() and is_hidden:
        assert file_name[0] == "."
    full_path = Path(folder, file_name)
    if propmtime.os_util.is_windows() and os.path.exists(full_path):
        win32api.SetFileAttributes(str(full_path), win32con.FILE_ATTRIBUTE_NORMAL)
    full_path.write_text(str(full_path.absolute()))  # just put something in the file ... this is as good as anything
    if propmtime.os_util.is_windows():
        if is_hidden:
            win32api.SetFileAttributes(str(full_path), win32con.FILE_ATTRIBUTE_HIDDEN)
        if is_system:
            win32api.SetFileAttributes(str(full_path), win32con.FILE_ATTRIBUTE_SYSTEM)
    mtime = time.time() - time_offset  # set file's mtime back in time
    os.utime(str(full_path), (mtime, mtime))
    return mtime
