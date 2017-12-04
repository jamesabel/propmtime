# PEP 440 compliant
# adhere to http://semver.org/
__version__ = '0.2.1'

# required for OSNAP
__author__ = 'abel'
__application_name__ = 'propmtime'
__python_version__ = '3.6.2'

__url__ = 'https://github.com/jamesabel/propmtime'

DB_EXTENSION = '.db'
TIMEOUT = 100  # seconds

from .logger import get_logger, init_logger, set_verbose
from .util import is_linux, is_mac, is_windows, get_file_attributes, get_long_abs_path
from .programmable_icon import get_icon
from .blink import set_blinking, init_blink, request_blink_exit
from .arguments import get_arguments
from .propmtime import PropMTime, init_propmtime_logger, propmtime_event, cli_main
from .preferences import Preferences
from .propmtime import PropMTime
from .scan import Scan
from .gui_paths import PathsDialog
from .gui_scan import ScanDialog
