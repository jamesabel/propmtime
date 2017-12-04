
import appdirs
import os

from PyQt5.QtWidgets import QDialogButtonBox, QLineEdit, QGridLayout, QDialog, QPushButton, QVBoxLayout, QGroupBox, QFileDialog, QLabel
from PyQt5.Qt import QApplication, QFontMetrics, QFont

from propmtime import get_logger, __application_name__, __author__, init_propmtime_logger, PropMTime, TIMEOUT
from propmtime import Preferences, get_arguments


"""
Displays a dialog box with the monitor paths.  Allows monitor paths to be added and/or deleted.
"""

log = get_logger(__application_name__)


class QScanPushButton(QPushButton):
    def __init__(self, path, label, app_data_folder):
        super().__init__('Scan')
        self._path = path
        self._label = label
        self._app_data_folder = app_data_folder

    def scan(self):
        pref = Preferences(self._app_data_folder)
        pmt = PropMTime(self._path, True, pref.get_do_hidden(), pref.get_do_system())
        pmt.start()
        pmt.join(TIMEOUT)


class ScanDialog(QDialog):
    def __init__(self, app_data_folder):
        log.info('starting PathsDialog')
        self._app_data_folder = app_data_folder
        self._paths_row = 0
        super().__init__()

        log.info('preferences folder : %s' % self._app_data_folder)
        preferences = Preferences(self._app_data_folder, True)

        self.setWindowTitle('Scan a Path')
        dialog_layout = QVBoxLayout()
        self.setLayout(dialog_layout)

        # paths
        paths_box = QGroupBox()
        paths_box.setWindowTitle('Paths')
        self._paths_layout = QGridLayout()
        paths_box.setLayout(self._paths_layout)
        for path in preferences.get_all_paths():
            self.add_path_row(path)
        dialog_layout.addWidget(paths_box)

        # ok
        standard_button_box = QGroupBox()
        standard_button_layout = QGridLayout()
        standard_button_box.setLayout(standard_button_layout)
        ok_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_buttonBox.accepted.connect(self.ok)

        standard_button_layout.addWidget(ok_buttonBox, 0, 0)
        dialog_layout.addWidget(standard_button_box)

    def add_path_row(self, path):
        path_line = QLineEdit(path)
        path_line.setReadOnly(True)
        width = QFontMetrics(QFont()).width(path) * 1.05
        path_line.setMinimumWidth(width)

        # path line
        self._paths_layout.addWidget(path_line, self._paths_row, 0)

        # scan button
        scan_button = QScanPushButton(path, path_line, self._app_data_folder)
        scan_button.clicked.connect(scan_button.scan)
        self._paths_layout.addWidget(scan_button, self._paths_row, 1)

        self._paths_row += 1

    def ok(self):
        self.close()

