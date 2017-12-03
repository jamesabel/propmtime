
import appdirs
import os

from PyQt5.QtWidgets import QDialogButtonBox, QLineEdit, QGridLayout, QDialog, QPushButton, QVBoxLayout, QGroupBox, QFileDialog, QLabel
from PyQt5.Qt import QApplication, QFontMetrics, QFont

from propmtime import get_logger, __application_name__, init_propmtime_logger
import propmtime.preferences


"""
Displays a dialog box with the monitor paths.  Allows monitor paths to be added and/or deleted.
"""

log = get_logger(__application_name__)


class QRemovePushButton(QPushButton):
    def __init__(self, path, label, removes, adds):
        super().__init__('Remove')
        self._path = path
        self._removes = removes
        self._adds = adds
        self._label = label

    def remove(self):
        if self._path in self._adds:
            self._adds.remove(self._path)
        self._removes.add(self._path)
        self.deleteLater()  # remove row associated with this path from dialog box
        self._label.deleteLater()


class PathsDialog(QDialog):
    def __init__(self, app_data_folder):
        log.info('starting PathsDialog')
        self._app_data_folder = app_data_folder
        self._paths_row = 0
        self._adds = set()  # paths to add to the preferences DB
        self._removes = set()  # paths to remove from the preferences DB
        super().__init__()

        log.info('preferences folder : %s' % self._app_data_folder)
        preferences = propmtime.preferences.Preferences(self._app_data_folder, True)

        self.setWindowTitle('Monitor Paths')
        dialog_layout = QVBoxLayout()
        self.setLayout(dialog_layout)

        # instructions
        instructions_box = QGroupBox()
        instructions_layout = QGridLayout()
        # unfortunately, currently if I watchdog monitor ~/Documents the initial watchdog schedule takes a really long time
        instructions_layout.addWidget(QLabel('Only add directories with a reasonable size and that do'))
        instructions_layout.addWidget(QLabel('not have links to big directories (watchdog follows links).'))
        instructions_box.setLayout(instructions_layout)
        dialog_layout.addWidget(instructions_box)

        # paths
        paths_box = QGroupBox()
        paths_box.setWindowTitle('Paths')
        self._paths_layout = QGridLayout()
        paths_box.setLayout(self._paths_layout)
        for path in preferences.get_all_paths():
            self.add_path_row(path)
        dialog_layout.addWidget(paths_box)

        # "add path" button
        add_box = QGroupBox()
        add_layout = QGridLayout()
        add_box.setLayout(add_layout)
        add_button = QPushButton('Add Path')
        add_button.clicked.connect(self.add_action)
        add_layout.addWidget(add_button, self._paths_row, 1)
        dialog_layout.addWidget(add_box)

        # ok/cancel
        standard_button_box = QGroupBox()
        standard_button_layout = QGridLayout()
        standard_button_box.setLayout(standard_button_layout)
        ok_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_buttonBox.accepted.connect(self.ok)
        cancel_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
        cancel_buttonBox.rejected.connect(self.cancel)
        standard_button_layout.addWidget(ok_buttonBox, 0, 0)
        standard_button_layout.addWidget(cancel_buttonBox, 0, 1)
        dialog_layout.addWidget(standard_button_box)

    def add_action(self):
        new_folder = QFileDialog.getExistingDirectory(parent=self, caption='Add Folder', options=QFileDialog.ShowDirsOnly, directory=os.path.expandvars('~'))
        if new_folder:
            if new_folder in self._removes:
                self._removes.remove(new_folder)
            self._adds.add(new_folder)
            self.add_path_row(new_folder)

    def add_path_row(self, path):
        path_line = QLineEdit(path)
        path_line.setReadOnly(True)
        width = QFontMetrics(QFont()).width(path) * 1.05
        path_line.setMinimumWidth(width)
        self._paths_layout.addWidget(path_line, self._paths_row, 0)
        button = QRemovePushButton(path, path_line, self._removes, self._adds)
        button.clicked.connect(button.remove)
        self._paths_layout.addWidget(button, self._paths_row, 1)
        self._paths_row += 1

    def ok(self):
        pref = propmtime.preferences.Preferences(self._app_data_folder)
        for add in self._adds:
            log.info('adding : %s' % add)
            if add not in pref.get_all_paths():
                pref.add_path(add)
        for remove in self._removes:
            log.info('removing : %s' % remove)
            pref.remove_path(remove)
        self.close()

    def cancel(self):
        self.close()


def main():
    import sys

    init_propmtime_logger()

    app = QApplication(sys.argv)

    app_data_folder = appdirs.user_config_dir(propmtime.__application_name__, propmtime.__author__)
    preferences_dialog = PathsDialog(app_data_folder)
    preferences_dialog.show()
    preferences_dialog.exec_()


if __name__ == '__main__':
    main()
