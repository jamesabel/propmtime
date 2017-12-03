
import sys
import appdirs

from PyQt5.QtGui import QFontMetrics, QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QSystemTrayIcon, QMenu, QDialog, QApplication

from propmtime import get_logger, __application_name__, init_propmtime_logger, set_verbose, TIMEOUT, get_arguments
import propmtime.preferences
import propmtime.gui_preferences
import propmtime.gui_paths
import propmtime.util
import propmtime.watcher

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
        self.scan_pmts = []
        pref = propmtime.preferences.Preferences(app_data_folder, True)
        set_verbose(pref.get_verbose())
        log.info('starting LatusSystemTrayIcon')
        log.info('preferences path : %s' % pref.get_db_path())
        self.app = app
        self.log_file_path = log_file_path

        from propmtime import icons
        icon = QIcon(QPixmap(':icon.png'))
        super().__init__(icon, parent)
        self._appdata_folder = app_data_folder

        menu = QMenu(parent)
        menu.addAction("Paths").triggered.connect(self.paths)
        menu.addAction("Scan").triggered.connect(self.scan)
        menu.addAction("Preferences").triggered.connect(self.preferences)
        menu.addAction("About").triggered.connect(self.about)
        menu.addAction("Exit").triggered.connect(self.exit)
        self.setContextMenu(menu)

        log.info('starting initial scan')

        # when we initially run, do a propmtime on all paths in our configuration
        self._init_pmts = []
        for path in pref.get_all_paths():
            pmt = propmtime.PropMTime(path, True, pref.get_do_hidden(), pref.get_do_system())
            pmt.start()
            self._init_pmts.append(pmt)

        log.info('initial scan complete')

        if pref.get_background_monitor():
            self._watcher = propmtime.watcher.Watcher(self._appdata_folder)
        else:
            self._watcher = None

    def paths(self):
        preferences_dialog = propmtime.gui_paths.PathsDialog(self._appdata_folder)
        preferences_dialog.exec_()

    def scan(self):
        log.info('starting scan')
        pref = propmtime.preferences.Preferences(self._appdata_folder)
        for pmt in self.scan_pmts:
            # if we're still scanning from a previous scan command, just return
            if pmt.isAlive():
                log.info('a scan is already running - not starting another')
                return
        self.scan_pmts = []
        for path in pref.get_all_paths():
            pmt = propmtime.PropMTime(path, True, pref.get_do_hidden(), pref.get_do_system())
            pmt.start()
            self.scan_pmts.append(pmt)
        log.info('scan complete')

    def preferences(self):
        preferences_dialog = propmtime.gui_preferences.PreferencesDialog(self._appdata_folder)
        preferences_dialog.exec_()

        for pmt in self._init_pmts:
            pmt.request_exit()
        for pmt in self._init_pmts:
            pmt.join(TIMEOUT)
            if pmt.isAlive():
                log.error('propmtime thread from init still alive')

    def about(self):
        about_box = About(self.log_file_path)
        about_box.exec()

    def exit(self):
        for pmt in self._init_pmts:
            pmt.request_exit()
        for pmt in self._init_pmts:
            pmt.join(TIMEOUT)
            if pmt.isAlive():
                log.error('propmtime thread from init still alive')
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
