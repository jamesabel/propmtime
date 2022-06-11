from pathlib import Path

from PyQt5.QtWidgets import QDialogButtonBox, QLineEdit, QGridLayout, QDialog, QPushButton, QVBoxLayout, QGroupBox
from PyQt5.Qt import QFontMetrics, QFont

from balsa import get_logger
from tobool import to_bool_strict

from propmtime import __application_name__
from propmtime.gui import get_propmtime_preferences, get_propmtime_paths

"""
Displays a dialog box with the monitor paths.  Allows monitor paths to be added and/or deleted.
"""

log = get_logger(__application_name__)


class QScanPushButton(QPushButton):
    def __init__(self, path: Path, label: str, system_tray):
        super().__init__("Scan")
        self._path = path
        self._label = label
        self._system_tray = system_tray

    def scan(self):
        log.info(f"manual scan of {self._path}")
        pref = get_propmtime_preferences()
        # use the system tray class to do the actual scan since it keeps track of the running scans
        self._system_tray.stop_scan()
        self._system_tray.scan_one(self._path, to_bool_strict(pref.process_hidden), to_bool_strict(pref.process_system), to_bool_strict(pref.process_dot_as_normal))


class ScanDialog(QDialog):
    def __init__(self, system_tray):
        log.debug("starting PathsDialog")
        self._system_tray = system_tray
        self._paths_row = 0
        super().__init__()

        self.setWindowTitle("Scan a Path")
        dialog_layout = QVBoxLayout()
        self.setLayout(dialog_layout)

        # paths
        paths_box = QGroupBox()
        paths_box.setWindowTitle("Paths")
        self._paths_layout = QGridLayout()
        paths_box.setLayout(self._paths_layout)
        for path in get_propmtime_paths().get():
            self.add_path_row(path)
        dialog_layout.addWidget(paths_box)

        # ok
        standard_button_box = QGroupBox()
        standard_button_layout = QGridLayout()
        standard_button_box.setLayout(standard_button_layout)
        ok_button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_button_box.accepted.connect(self.ok)

        standard_button_layout.addWidget(ok_button_box, 0, 0)
        dialog_layout.addWidget(standard_button_box)

    def add_path_row(self, path):
        path_line = QLineEdit(path)
        path_line.setReadOnly(True)
        width = QFontMetrics(QFont()).width(path) * 1.05
        path_line.setMinimumWidth(int(round(width)))

        # path line
        self._paths_layout.addWidget(path_line, self._paths_row, 0)

        # scan button
        scan_button = QScanPushButton(path, path_line.text(), self._system_tray)
        scan_button.clicked.connect(scan_button.scan)
        self._paths_layout.addWidget(scan_button, self._paths_row, 1)

        self._paths_row += 1

    def ok(self):
        self.close()
