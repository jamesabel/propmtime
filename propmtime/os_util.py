import functools
import os
import platform
from pathlib import Path
from platform import architecture
from typing import Tuple, Union

import win32api
import win32con

from typeguard import typechecked

from balsa import get_logger
from propmtime import __application_name__


log = get_logger(__application_name__)

special_system_files = ["Thumbs.db",  # Windows thumbs but somehow isn't always a system or hidden file
                        ".DS_Store"  # This supposedly Apple macOS file seems to make it into lots of places
                        ]


@typechecked(always=True)
def get_target_os() -> (str, None):
    if is_windows():
        bit_string, os_string = architecture()
        target_os = f"{os_string[0:3].lower()}{bit_string[0:2]}"
    else:
        target_os = None
    return target_os


def get_file_attributes(in_path: Path) -> Tuple[bool, bool]:
    hidden = False
    system = False
    if in_path.is_file() and in_path.name in special_system_files:
        system = True
    if is_windows():
        attrib = 0
        try:
            attrib = win32api.GetFileAttributes(os.fspath(in_path))
        except Exception as e:
            log.info("%s : %s" % (in_path, str(e)))
        if attrib & win32con.FILE_ATTRIBUTE_HIDDEN:
            hidden = True
        if attrib & win32con.FILE_ATTRIBUTE_SYSTEM:
            system = True
    elif is_mac() or is_linux():
        if "/." in in_path:
            hidden = True
        else:
            name = in_path.name
            if name is not None and len(name) > 0:
                if name[0] == ".":
                    hidden = True
                # in Mac, there's a file named 'Icon\r' that we want to ignore
                # see http://superuser.com/questions/298785/icon-file-on-os-x-desktop
                if (name == "Icon\r") or (name == "Icon\n"):
                    hidden = True
    else:
        raise NotImplementedError
    return hidden, system


def get_long_abs_path(in_path_parameter: Union[Path, str, None]) -> Union[Path, None]:
    if in_path_parameter is None:
        abs_path = None
    elif is_windows():
        # https://twitter.com/brettsky/status/1404521184008413184
        in_path = os.fspath(in_path_parameter)

        # Trick to get around 260 char limit
        # http://msdn.microsoft.com/en-us/library/aa365247.aspx#maxpath
        long_prefix = "\\\\?\\"
        prefix_len = len(long_prefix)
        starts_with = in_path[:4].startswith(long_prefix)
        if is_windows() and ((len(in_path) < prefix_len) or not starts_with):
            abs_path_str = long_prefix + os.path.abspath(in_path)
        else:
            abs_path_str = os.path.abspath(in_path)
        if os.path.isdir(abs_path_str):
            abs_path_str += os.sep

        abs_path = Path(abs_path_str)
    else:
        abs_path = Path(in_path_parameter).absolute()

    return abs_path


@functools.lru_cache()  # platform doesn't change
def is_mac() -> bool:
    # darwin
    return platform.system().lower()[0] == "d"


@functools.lru_cache()  # platform doesn't change
def is_linux() -> bool:
    return platform.system().lower()[0] == "l"


@functools.lru_cache()  # platform doesn't change
def is_windows() -> bool:
    return platform.system().lower()[0] == "w"
