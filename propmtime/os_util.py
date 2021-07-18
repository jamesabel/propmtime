import distutils.util
import functools
import os
import platform
import shutil
import time
from pathlib import Path
import stat
from platform import architecture
from typing import Tuple, Union

import win32api
import win32con

from typeguard import typechecked

from balsa import get_logger
from propmtime import __application_name__


log = get_logger(__application_name__)


@typechecked(always=True)
def get_target_os() -> (str, None):
    if is_windows():
        bit_string, os_string = architecture()
        target_os = f"{os_string[0:3].lower()}{bit_string[0:2]}"
    else:
        target_os = None
    return target_os


@typechecked(always=True)
def remove_readonly(path: Path):
    os.chmod(str(path), stat.S_IWRITE)


# sometimes needed for Windows
def _remove_readonly_onerror(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


@typechecked(always=True)
def rmdir(p: Path, log_function=log.error) -> bool:
    retry_count = 0
    retry_limit = 4
    delete_ok = False
    delay = 1.0
    while p.exists() and retry_count < retry_limit:
        try:
            shutil.rmtree(p, onerror=_remove_readonly_onerror)
            delete_ok = True
        except FileNotFoundError as e:
            log.debug(str(e))  # this can happen when first doing the shutil.rmtree()
            time.sleep(delay)
        except PermissionError as e:
            log.info(str(e))
            time.sleep(delay)
        except OSError as e:
            log.info(str(e))
            time.sleep(delay)
        time.sleep(0.1)
        if p.exists:
            time.sleep(delay)
        retry_count += 1
        delay *= 2.0
    if p.exists():
        log_function(f"could not remove {p} ({retry_count=})", stack_info=True)
    else:
        delete_ok = True
    return delete_ok


@typechecked(always=True)
def mkdirs(d: Path, remove_first: bool = False, log_function=log.error):
    """
    make directories recursively, optionally deleting first
    :param d: directory to make
    :param remove_first: True to delete directory contents first
    :param log_function: log function
    """
    if remove_first:
        rmdir(d, log_function)
    # sometimes when os.makedirs exits the dir is not actually there
    count = 600
    while count > 0 and not d.exists():
        try:
            # for some reason we can get the FileNotFoundError exception
            d.mkdir(parents=True, exist_ok=True)
        except FileNotFoundError:
            pass
        if not d.exists():
            time.sleep(0.1)
        count -= 1
    if not d.exists():
        log_function(f'could not mkdirs "{d}" ({d.absolute()})')


@typechecked(always=True)
def copy_tree(source: Path, dest: Path, subdir: str):
    # copy the tree, but don't copy things like __pycache__
    dest.mkdir(parents=True, exist_ok=True)
    source = Path(source, subdir)
    dest = Path(dest, subdir)
    shutil.copytree(str(source), str(dest), ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)


def get_file_attributes(in_path: Path) -> Tuple[bool, bool]:
    hidden = False
    system = False
    if in_path.is_file() and in_path.name == ".DS_Store":
        # special case - this supposedly Apple macOS file seems to make it into lots of places
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
def is_mac():
    # darwin
    return platform.system().lower()[0] == "d"


@functools.lru_cache()  # platform doesn't change
def is_linux():
    return platform.system().lower()[0] == "l"


@functools.lru_cache()  # platform doesn't change
def is_windows():
    return platform.system().lower()[0] == "w"
