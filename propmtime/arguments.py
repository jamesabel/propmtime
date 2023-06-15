import argparse
import textwrap
import inspect

import appdirs

from balsa import get_logger

from propmtime import __application_name__, __author__

log = get_logger(__application_name__)


def log_selections(args):
    for a in sorted(inspect.getmembers(args)):
        if not a[0].startswith("_"):
            log.info("args : %s" % str(a))


def get_arguments():
    desc = textwrap.dedent(
        """
Most OSs (including Windows and MacOS) only change the modification time of a folder/directory based on its immediate
children.  propmtime analyzes a folder and all of its children, and propagates (updates) the modification times of
each folder to be the most recent time of all of its children.

Author: James Abel
URL: https://github.com/jamesabel/propmtime
LICENSE: GPLv3"""
    )

    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", "--path", default=".", help='Path to folder or directory. (default=".")')
    parser.add_argument("-s", "--silent", action="store_true", default=False, help="Do not produce summary output (default=False)")
    parser.add_argument("--hidden", action="store_true", help="Process hidden files (default=False)", default=False)
    parser.add_argument("--system", action="store_true", help="Process system files (default=False)", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity (default=False)")
    parser.add_argument(
        "-l",
        "--logdir",
        default=appdirs.user_log_dir(
            __application_name__,
            __author__,
        ),
        help="Set the log directory (default from appdirs)",
    )
    parser.add_argument("-d", "--dellog", action="store_true", default=False, help="Delete existing log files on invocation (default=False)")
    parser.add_argument("-n", "--noupdate", action="store_true", default=False, help='Suppress updating the mtime (do a "dry run") (default=False)')
    args = parser.parse_args()

    return args
