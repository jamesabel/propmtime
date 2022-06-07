# PEP 440 compliant
# adhere to http://semver.org/
__version__ = "0.8.0"

__author__ = "abel"
__application_name__ = "propmtime"

__url__ = "https://github.com/jamesabel/propmtime"

DB_EXTENSION = ".db"
TIMEOUT = 100  # seconds

from .os_util import get_file_attributes, get_long_abs_path, is_mac, is_linux, is_windows
from .arguments import get_arguments, log_selections
from .exit_control import init_exit_control_cli, is_exit_requested
from .proptime_event_module import propmtime_event, _do_propagation, PropMTime
from .exit_control import request_exit_via_event, init_exit_control_event
