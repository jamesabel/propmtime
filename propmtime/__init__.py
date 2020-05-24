# PEP 440 compliant
# adhere to http://semver.org/
__version__ = '0.5.3'

# required for OSNAP
__author__ = 'abel'
__application_name__ = 'propmtime'
__python_version__ = '3.6.6'

__url__ = 'https://github.com/jamesabel/propmtime'

DB_EXTENSION = '.db'
TIMEOUT = 100  # seconds

from .os_util import get_file_attributes, get_long_abs_path, convert_to_bool, is_mac, is_linux, is_windows
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
