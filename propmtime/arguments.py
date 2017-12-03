
import argparse

import appdirs

from propmtime import __application_name__, __author__


def arguments():
    desc = """Many OSs (including Windows) only change the modification time of a folder/directory based on its immediate children.
    This code analyzes a folder and all of its children, and propagates (changes) the modification times of each folder to
    be the most recent time of all of its children."""
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--dellog', action='store_true', default=False,
                        help='delete existing log files on invocation')
    parser.add_argument('-n', '--noupdate', action='store_true', default=False, help='Supress updating the mtime')
    parser.add_argument("-l", "--logdir", default=appdirs.user_log_dir(__application_name__, __author__, ),
                        help='log directory.  (default from appdirs)')
    parser.add_argument("-p", "--path", default=".", help='Path to folder or directory.  (default=".")')
    parser.add_argument('--hidden', action='store_true', default=False)
    parser.add_argument('--system', action='store_true', default=False)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    return parser.parse_args()
