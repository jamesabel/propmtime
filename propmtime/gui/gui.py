import sys
import appdirs

from PyQt5.QtGui import QFontMetrics, QFont
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QSystemTrayIcon, QMenu, QDialog, QApplication

from balsa import get_logger, Balsa
import requests
from requests.exceptions import ConnectionError

from propmtime import __application_name__, __version__, __url__, __author__, request_exit_via_event
from propmtime import init_exit_control_event
from propmtime import TIMEOUT, PropMTimePreferences, PreferencesDialog, PropMTimeWatcher, get_arguments, PropMTime
from propmtime import get_icon, init_blink, request_blink_exit, PathsDialog, ScanDialog, init_preferences_db

log = get_logger(__application_name__)


class About(QDialog):
    def __init__(self, log_file_path):
        super().__init__()  # todo: fill in parameter?
        self.setWindowTitle(__application_name__)
        layout = QGridLayout(self)
        self.setLayout(layout)
        self.add_line("Version:", __version__, 1, layout)
        self.add_line("Source:", __url__, 3, layout)
        self.add_line("Logs:", log_file_path, 5, layout)
        self.show()

    def add_line(self, label, value, row_number, layout):
        layout.addWidget(QLabel(label), row_number, 0)
        log_dir_widget = QLineEdit(value)
        log_dir_widget.setReadOnly(True)
        width = QFontMetrics(QFont()).width(value) * 1.05
        log_dir_widget.setMinimumWidth(width)
        layout.addWidget(log_dir_widget, row_number + 1, 0)


class PropMTimeSystemTray(QSystemTrayIcon):

    update_tool_tip_signal = pyqtSignal(bool)

    def __init__(self, app, app_data_folder, log_file_path, parent=None):

        super().__init__(get_icon(False), parent)

        self.update_tool_tip_signal.connect(self.update_tool_tip)

        pref = PropMTimePreferences(app_data_folder)
        log.info("preferences path : %s" % pref.get_db_path())

        self.app = app
        self.log_file_path = log_file_path
        self._app_data_folder = app_data_folder

        menu = QMenu(parent)
        menu.addAction("Scan").triggered.connect(self.scan)
        menu.addAction("Scan All").triggered.connect(self.scan_all)
        menu.addAction("Stop Scan").triggered.connect(self.stop_scan)
        menu.addAction("Set Paths").triggered.connect(self.set_paths)
        menu.addAction("Preferences").triggered.connect(self.preferences)
        menu.addAction("About").triggered.connect(self.about)
        menu.addAction("Exit").triggered.connect(self.exit)
        self.setContextMenu(menu)

        self._watcher = PropMTimeWatcher(self._app_data_folder)

        self._scanners = []

        init_blink(self)

        self.update_tool_tip(False)

    def update_tool_tip(self, running: bool):
        if running:
            tool_tip_string = "Running"
        else:
            tool_tip_string = "Ready"
        self.setToolTip(tool_tip_string)

    def scan_all(self):
        self.stop_scan()  # if any scans are running, stop them first
        log.debug("scan_all started : %s" % self._app_data_folder)
        pref = PropMTimePreferences(self._app_data_folder)
        paths = pref.get_all_paths()
        do_hidden = pref.get_do_hidden()
        do_system = pref.get_do_system()
        process_dot_folders_as_normal = pref.get_process_dot_folders_as_normal()
        log.debug("paths : %s" % paths)
        for path in paths:
            self.scan_one(path, do_hidden, do_system, process_dot_folders_as_normal)

    def scan(self):
        scan_dialog = ScanDialog(self._app_data_folder, self)
        scan_dialog.exec_()

    def scan_one(self, path, do_hidden: bool, do_system: bool, process_dot_folders_as_normal: bool):
        self.update_tool_tip(True)
        log.debug(f"scan_one : {path,do_hidden,do_system}")
        scanner = PropMTime(path, True, do_hidden, do_system, process_dot_folders_as_normal, self.update_tool_tip_signal.emit)
        scanner.start()
        log.debug(f"scan started : {path}")
        self._scanners.append(scanner)

    def stop_scan(self):
        request_exit_via_event()  # tell all current scans to stop (if any)
        self.join_scans()  # wait for them to stop
        init_exit_control_event()  # re-init the exit control we just set

    def set_paths(self):
        paths_dialog = PathsDialog(self._app_data_folder)
        paths_dialog.exec_()

    def join_scans(self):
        # join scans in process
        log.debug(f"waiting for {len(self._scanners)} scan threads")
        for scanner in self._scanners:
            scanner.join(TIMEOUT)
        for scanner in self._scanners:
            if scanner.is_alive():
                log.warning("could not stop : %s" % str(scanner))
        log.debug("all scan threads have been joined")
        self._scanners = []  # all existing scan threads have finished

    def preferences(self):
        # don't change things in the middle of a scan
        request_exit_via_event()
        self.join_scans()
        preferences_dialog = PreferencesDialog(self._app_data_folder)
        preferences_dialog.exec_()
        # todo: update log verbosity (when balsa adds that capability)
        init_exit_control_event()

    def about(self):
        about_box = About(self.log_file_path)
        about_box.exec()

    def exit(self):
        log.info("exit")
        self.stop_scan()  # stop any scans currently underway
        request_blink_exit()
        if self._watcher:
            self._watcher.request_exit()
        self.hide()
        QApplication.exit()  # todo: what should this parameter be?


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
    system_tray.show()
    app.exec_()
