
import platform
import os
import win32api
import win32con
import pywintypes

WINDOWS_SEP = "\\"
LINUX_SEP = '/'


def get_folder_sep():
    if is_windows():
        sep = WINDOWS_SEP
    else:
        sep = LINUX_SEP
    return sep[-1]


def get_file_attributes(in_path, verbose):
    attrib = 0
    attributes = set()
    if is_windows():
        try:
            attrib = win32api.GetFileAttributes(in_path)
        except pywintypes.error as e:
            if verbose:
                print(e, in_path)
        if attrib & win32con.FILE_ATTRIBUTE_HIDDEN:
            attributes.add(win32con.FILE_ATTRIBUTE_HIDDEN)
        if attrib & win32con.FILE_ATTRIBUTE_SYSTEM:
            attributes.add(win32con.FILE_ATTRIBUTE_SYSTEM)
    # todo : Linux version of this
    return attributes


def is_windows():
    is_win = False
    plat = platform.system()
    plat = plat.lower()
    if plat[0] == 'w':
        is_win = True
    return is_win


def get_long_abs_path(in_path):
    if in_path is None:
        return None
    # Trick to get around 260 char limit
    # http://msdn.microsoft.com/en-us/library/aa365247.aspx#maxpath
    long_prefix = "\\\\?\\"
    prefix_len = len(long_prefix)
    starts_with = in_path[:4].startswith(long_prefix)
    if is_windows() and ((len(in_path) < prefix_len) or not starts_with):
        abs_path = long_prefix + os.path.abspath(in_path)
    else:
        abs_path = os.path.abspath(in_path)
    if os.path.isdir(abs_path):
        abs_path += get_folder_sep()
    return abs_path