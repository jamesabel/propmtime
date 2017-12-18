# PEP 440 compliant
# adhere to http://semver.org/
__version__ = '0.3.0'

# required for OSNAP
__author__ = 'abel'
__application_name__ = 'propmtime'
__python_version__ = '3.6.2'

__url__ = 'https://github.com/jamesabel/propmtime'

DB_EXTENSION = '.db'
TIMEOUT = 100  # seconds

from .logger import get_logger, init_logger, set_verbose, init_logger_from_args
from .util import is_linux, is_mac, is_windows, get_file_attributes, get_long_abs_path
from propmtime.gui import icons
from propmtime.gui.programmable_icon import get_icon
from propmtime.gui.blink import set_blinking, init_blink, request_blink_exit
from .arguments import get_arguments, log_selections
from propmtime.gui.preferences import PropMTimePreferences, init_preferences_db
from propmtime.gui.gui_preferences import PreferencesDialog
from .exit_control import init_exit_control_cli, is_exit_requested
from propmtime.exit_control import request_exit_via_event, init_exit_control_event
from .propmtime import PropMTime, propmtime_event, cli_main
from propmtime.gui.watcher import PropMTimeWatcher
from propmtime.gui.gui_paths import PathsDialog
from propmtime.gui.gui_scan import ScanDialog
from propmtime.gui.gui import gui_main
