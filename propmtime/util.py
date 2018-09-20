
import distutils.util

from balsa import get_logger

import platform
import os
import functools

from propmtime import __application_name__

log = get_logger(__application_name__)


@functools.lru_cache()  # platform doesn't change
def is_windows():
    return platform.system().lower()[0] == 'w'


@functools.lru_cache()  # platform doesn't change
def is_linux():
    return platform.system().lower()[0] == 'l'


@functools.lru_cache()  # platform doesn't change
def is_mac():
    # darwin
    return platform.system().lower()[0] == 'd'


if is_windows():
    import win32api
    import win32con


def get_file_attributes(in_path):
    hidden = False
    system = False
    if is_windows():
        attrib = 0
        try:
            attrib = win32api.GetFileAttributes(in_path)
        except Exception as e:
            log.info('%s : %s' % (in_path, str(e)))
        if attrib & win32con.FILE_ATTRIBUTE_HIDDEN:
            hidden = False
        if attrib & win32con.FILE_ATTRIBUTE_SYSTEM:
            system = False
    elif is_mac() or is_linux():
        if '/.' in in_path:
            hidden = True
        else:
            basename = os.path.basename(in_path)
            if len(basename) > 0:
                if basename[0] == '.':
                    hidden = True
                # in Mac, there's a file named 'Icon\r' that we want to ignore
                # see http://superuser.com/questions/298785/icon-file-on-os-x-desktop
                if (basename == 'Icon\r') or (basename == 'Icon\n'):
                    hidden = True
    else:
        raise NotImplementedError
    return hidden, system


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
        abs_path += os.sep
    return abs_path


def convert_to_bool(orig_input):
    """
    performs a casting of a multitude of things (string, int, etc.) to bool.
    :param orig_input: original variable
    :return: boolean value of input variable, if possible
    """

    if isinstance(orig_input, int) and 0 <= orig_input <= 1:
        new_bool = bool(orig_input)  # 0, 1
    elif isinstance(orig_input, bool):
        new_bool = orig_input  # pass through
    elif orig_input is None:
        new_bool = False  # along the lines of Python's truthiness
    elif isinstance(orig_input, str):
        new_bool = bool(distutils.util.strtobool(orig_input))  # strtobool returns an int
    else:
        log.error(f"could not convert {orig_input} to a boolean")
        new_bool = None

    return new_bool
