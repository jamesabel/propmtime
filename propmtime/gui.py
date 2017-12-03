
import sys

from PyQt5.QtGui import QFontMetrics, QFont
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QSystemTrayIcon, QMenu, QDialog, QApplication

from propmtime import get_logger, __application_name__, init_propmtime_logger, set_verbose, get_arguments
import propmtime.preferences
import propmtime.gui_preferences
import propmtime.gui_paths
import propmtime.util
import propmtime.watcher
from propmtime import get_icon, Scan, init_blink, request_blink_exit

log = get_logger(__application_name__)


class About(QDialog):

    def __init__(self, log_file_path):
        super().__init__()  # todo: fill in parameter?
        self.setWindowTitle(__application_name__)
        layout = QGridLayout(self)
        self.setLayout(layout)
        self.add_line('Version:', propmtime.__version__, 1, layout)
        self.add_line('Source:', propmtime.__url__, 3, layout)
        self.add_line('Logs:', log_file_path, 5, layout)
        self.show()

    def add_line(self, label, value, row_number, layout):
        layout.addWidget(QLabel(label), row_number, 0)
        log_dir_widget = QLineEdit(value)
        log_dir_widget.setReadOnly(True)
        width = QFontMetrics(QFont()).width(value) * 1.05
        log_dir_widget.setMinimumWidth(width)
        layout.addWidget(log_dir_widget, row_number+1, 0)


class PropMTimeSystemTray(QSystemTrayIcon):
    def __init__(self, app, app_data_folder, log_file_path, parent=None):
        pref = propmtime.preferences.Preferences(app_data_folder, True)
        set_verbose(pref.get_verbose())
        log.info('starting LatusSystemTrayIcon')
        log.info('preferences path : %s' % pref.get_db_path())
        self.app = app
        self.log_file_path = log_file_path

        super().__init__(get_icon(False), parent)
        self._appdata_folder = app_data_folder

        menu = QMenu(parent)
        menu.addAction("Paths").triggered.connect(self.paths)
        menu.addAction("Scan All").triggered.connect(self.scan)
        menu.addAction("Preferences").triggered.connect(self.preferences)
        menu.addAction("About").triggered.connect(self.about)
        menu.addAction("Exit").triggered.connect(self.exit)
        self.setContextMenu(menu)

        if pref.get_background_monitor():
            self._watcher = propmtime.watcher.Watcher(self._appdata_folder)
        else:
            self._watcher = None

        self.scanner = None

        init_blink(self)

        if pref.get_background_monitor():
            self.scan()

    def scan(self):
        self.scanner = Scan(self._appdata_folder)
        self.scanner.start()

    def paths(self):
        preferences_dialog = propmtime.gui_paths.PathsDialog(self._appdata_folder)
        preferences_dialog.exec_()

    def stop_scans(self):
        if self.scanner:
            self.scanner.request_exit()

    def preferences(self):
        self.stop_scans()  # don't change things in the middle of a scan
        preferences_dialog = propmtime.gui_preferences.PreferencesDialog(self._appdata_folder)
        preferences_dialog.exec_()

    def about(self):
        about_box = About(self.log_file_path)
        about_box.exec()

    def exit(self):
        request_blink_exit()
        self.stop_scans()
        if self._watcher:
            self._watcher.request_exit()
        log.info('exit')
        self.hide()
        QApplication.exit()  # todo: what should this parameter be?


def main(app_data_folder):

    log, handlers, log_file_path = init_propmtime_logger(get_arguments())

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # so popup dialogs don't close the system tray icon
    system_tray = PropMTimeSystemTray(app, app_data_folder, log_file_path)
    system_tray.show()
    app.exec_()
