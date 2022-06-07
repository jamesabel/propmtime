import os
from pathlib import Path
from typing import Set

from PyQt5.QtWidgets import QDialogButtonBox, QLineEdit, QGridLayout, QDialog, QPushButton, QVBoxLayout, QGroupBox, QFileDialog, QLabel
from PyQt5.Qt import QFontMetrics, QFont, QCheckBox

from balsa import get_logger

from propmtime import __application_name__
from propmtime.gui import PropMTimePreferences


"""
Displays a dialog box with the monitor paths.  Allows monitor paths to be added and/or deleted.
"""

log = get_logger(__application_name__)


class QRemovePushButton(QPushButton):
    def __init__(self, path, path_line, watch_label, watch_check, removes, adds):
        super().__init__("Remove")
        self._path = path
        self._removes = removes
        self._adds = adds
        self._path_line = path_line
        self._watch_label = watch_label
        self._watch_check = watch_check

    def remove(self):
        if self._path in self._adds:
            self._adds.remove(self._path)
        self._removes.add(self._path)
        self.deleteLater()  # remove row associated with this path from dialog box
        self._path_line.deleteLater()
        self._watch_label.deleteLater()
        self._watch_check.deleteLater()


class PathsDialog(QDialog):
    def __init__(self, app_data_folder):
        log.info("starting PathsDialog")
        self._app_data_folder = app_data_folder
        self._paths_row = 0
        # paths to add to the preferences DB
        self._adds = set()  # type: Set[Path]
        # paths to remove from the preferences DB
        self._removes = set()  # type: Set[Path]
        self._watch_check_boxes = {}
        super().__init__()

        log.info("preferences folder : %s" % self._app_data_folder)
        pref = PropMTimePreferences(self._app_data_folder)

        self.setWindowTitle("Monitor Paths")
        dialog_layout = QVBoxLayout()
        self.setLayout(dialog_layout)

        # instructions
        instructions_box = QGroupBox()
        instructions_layout = QGridLayout()
        instructions_layout.addWidget(QLabel("Only add directories with a reasonable size and that do"))
        instructions_layout.addWidget(QLabel("not have links to big directories (%s follows links)." % __application_name__))
        instructions_box.setLayout(instructions_layout)
        dialog_layout.addWidget(instructions_box)

        # paths
        paths_box = QGroupBox()
        paths_box.setWindowTitle("Paths")
        self._paths_layout = QGridLayout()
        paths_box.setLayout(self._paths_layout)
        for path, watched in pref.get_all_paths().items():
            self.add_path_row(path, watched)
        dialog_layout.addWidget(paths_box)

        # "add path" button
        add_box = QGroupBox()
        add_layout = QGridLayout()
        add_box.setLayout(add_layout)
        add_button = QPushButton("Add Path")
        add_button.clicked.connect(self.add_action)
        add_layout.addWidget(add_button, self._paths_row, 1)
        dialog_layout.addWidget(add_box)

        # ok/cancel
        standard_button_box = QGroupBox()
        standard_button_layout = QGridLayout()
        standard_button_box.setLayout(standard_button_layout)
        ok_button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_button_box.accepted.connect(self.ok)
        cancel_button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        cancel_button_box.rejected.connect(self.cancel)
        standard_button_layout.addWidget(ok_button_box, 0, 0)
        standard_button_layout.addWidget(cancel_button_box, 0, 1)
        dialog_layout.addWidget(standard_button_box)

    def add_action(self):
        new_folder = Path(QFileDialog.getExistingDirectory(parent=self, caption="Add Folder", options=QFileDialog.ShowDirsOnly, directory=os.path.expandvars("~")))
        if new_folder:
            if new_folder in self._removes:
                self._removes.remove(new_folder)
            self._adds.add(new_folder)
            self.add_path_row(new_folder, False)

    def add_path_row(self, path: Path, watched):

        # path
        path = str(path)
        path_line = QLineEdit(path)
        path_line.setReadOnly(True)
        width = QFontMetrics(QFont()).width(path) * 1.05
        path_line.setMinimumWidth(int(round(width)))
        self._paths_layout.addWidget(path_line, self._paths_row, 0)

        # watch label and checkbox
        watcher_label = QLabel("watch:")
        self._paths_layout.addWidget(watcher_label, self._paths_row, 1)
        watcher_check_box = QCheckBox()
        watcher_check_box.setChecked(watched)
        self._watch_check_boxes[path] = watcher_check_box
        self._paths_layout.addWidget(watcher_check_box, self._paths_row, 2)

        # remove button
        remove_button = QRemovePushButton(path, path_line, watcher_label, watcher_check_box, self._removes, self._adds)
        remove_button.clicked.connect(remove_button.remove)
        self._paths_layout.addWidget(remove_button, self._paths_row, 3)

        self._paths_row += 1

    def ok(self):
        pref = PropMTimePreferences(self._app_data_folder)
        for add in self._adds:
            log.info("adding : %s" % add)
            if add not in pref.get_all_paths():
                pref.add_path(add)
        for remove in self._removes:
            log.info("removing : %s" % remove)
            pref.remove_path(remove)
        for path, watch_check_box in self._watch_check_boxes.items():
            if path not in self._removes:
                is_checked = watch_check_box.isChecked()
                if pref.is_path_watched(path) != is_checked:
                    pref.set_path_watched(path, is_checked)
        self.close()

    def cancel(self):
        self.close()
