import sys
import signal
from os import getpid

from ismain import is_main
import requests
from requests.exceptions import ConnectionError
import appdirs
from balsa import Balsa, get_logger
from PyQt5.QtWidgets import QApplication

from propmtime import get_arguments, __application_name__, __author__, init_exit_control_event
from propmtime.gui import PropMTimePreferences, init_preferences_db, PropMTimeSystemTray

log = get_logger(__application_name__)


def gui_main():

    args = get_arguments()

    sentry_dsn_url = r"https://api.abel.co/apps/propmtime/sentrydsn"
    sentry_dsn_issue = None
    try:
        sentry_dsn = requests.get(sentry_dsn_url).text
        if not (sentry_dsn.startswith("http") and "@sentry.io" in sentry_dsn):
            sentry_dsn = None
            sentry_dsn_issue = f"{sentry_dsn} not a valid Sentry DSN"
    except ConnectionError:
        sentry_dsn = None
        sentry_dsn_issue = f"ConnectionError on Sentry DSN : {sentry_dsn_url}"

    app_data_folder = appdirs.user_config_dir(appname=__application_name__, appauthor=__author__)
    init_preferences_db(app_data_folder)
    preferences = PropMTimePreferences(app_data_folder)

    balsa = Balsa(__application_name__, __author__, gui=True)
    if sentry_dsn is not None:
        balsa.use_sentry = True
        balsa.sentry_dsn = sentry_dsn
    balsa.verbose = preferences.get_verbose()
    balsa.init_logger_from_args(args)

    log.info(f"Sentry DSN URL : {sentry_dsn_url}")
    log.info(f"Sentry DSN : {sentry_dsn}")
    log.info(f"sentry_dsn_issue : {sentry_dsn_issue}")

    init_exit_control_event()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # so popup dialogs don't close the system tray icon
    system_tray = PropMTimeSystemTray(app, app_data_folder, balsa.log_path)
    log.info(f"{getpid()=}")
    signal.signal(signal.SIGBREAK, system_tray.exit)
    system_tray.show()
    app.exec_()


if is_main():
    gui_main()
