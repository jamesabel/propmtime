# PEP 440 compliant
# adhere to http://semver.org/
__version__ = '0.1.2'

# required for OSNAP
__author__ = 'abel'
__application_name__ = 'propmtime'
__python_version__ = '3.6.2'

__url__ = 'https://github.com/jamesabel/propmtime'

DB_EXTENSION = '.db'
TIMEOUT = 100  # seconds

from .logger import get_logger, init_logger, set_verbose
from .arguments import get_arguments
from .util import is_linux, is_mac, is_windows, get_file_attributes, get_long_abs_path
from .propmtime import PropMTime, init_propmtime_logger, propmtime_event, cli_main

