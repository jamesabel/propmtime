
import sys
import appdirs

from PyQt5.QtGui import QFontMetrics, QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QSystemTrayIcon, QMenu, QDialog, QApplication

import propmtime
import propmtime.logger
import propmtime.preferences
import propmtime.gui_preferences
import propmtime.gui_paths
import propmtime.util
import propmtime.watcher
import propmtime.const


class About(QDialog):

    def __init__(self):
        super().__init__()  # todo: fill in parameter?
        self.setWindowTitle(propmtime.__application_name__)
        layout = QGridLayout(self)
        self.setLayout(layout)
        self.add_line('Source:', propmtime.__url__, 1, layout)
        self.add_line('Logs:', propmtime.logger.get_base_log_file_path(), 3, layout)
        self.show()

    def add_line(self, label, value, row_number, layout):
        layout.addWidget(QLabel(label), row_number, 0)
        log_dir_widget = QLineEdit(value)
        log_dir_widget.setReadOnly(True)
        width = QFontMetrics(QFont()).width(value) * 1.05
        log_dir_widget.setMinimumWidth(width)
        layout.addWidget(log_dir_widget, row_number+1, 0)


class PropMTimeSystemTray(QSystemTrayIcon):
    def __init__(self, app, app_data_folder, parent=None):
        pref = propmtime.preferences.Preferences(app_data_folder, True)
        if pref.get_verbose():
            propmtime.util.set_verbose_logging()
        propmtime.logger.log.info('starting LatusSystemTrayIcon')
        propmtime.logger.log.info('preferences path : %s' % pref.get_db_path())
        self.app = app

        from propmtime import icons
        icon = QIcon(QPixmap(':icon.png'))
        super().__init__(icon, parent)
        self._appdata_folder = app_data_folder

        menu = QMenu(parent)
        menu.addAction("Paths").triggered.connect(self.paths)
        menu.addAction("Preferences").triggered.connect(self.preferences)
        menu.addAction("About").triggered.connect(self.about)
        menu.addAction("Exit").triggered.connect(self.exit)
        self.setContextMenu(menu)

        # when we initially run, do a propmtime on all paths in our configuration
        self._init_pmts = []
        for path in pref.get_all_paths():
            pmt = propmtime.PropMTime(path, True, pref.get_do_hidden(), pref.get_do_system())
            pmt.start()
            self._init_pmts.append(pmt)

        self._watcher = propmtime.watcher.Watcher(self._appdata_folder)

    def paths(self):
        preferences_dialog = propmtime.gui_paths.PathsDialog(self._appdata_folder)
        preferences_dialog.exec_()

    def preferences(self):
        preferences_dialog = propmtime.gui_preferences.PreferencesDialog(self._appdata_folder)
        preferences_dialog.exec_()

    def about(self):
        about_box = About()
        about_box.exec()

    def exit(self):
        for pmt in self._init_pmts:
            pmt.request_exit()
        for pmt in self._init_pmts:
            pmt.join(propmtime.const.TIMEOUT)
            if pmt.isAlive():
                propmtime.logger.log.error('propmtime thread from init still alive')
        self._watcher.request_exit()
        propmtime.logger.log.info('exit')
        self.hide()
        QApplication.exit()  # todo: what should this parameter be?


def main(app_data_folder):
    propmtime.logger.init(appdirs.user_log_dir(appname=propmtime.__application_name__, appauthor=propmtime.__author__))

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # so popup dialogs don't close the system tray icon
    system_tray = PropMTimeSystemTray(app, app_data_folder)
    system_tray.show()
    app.exec_()
