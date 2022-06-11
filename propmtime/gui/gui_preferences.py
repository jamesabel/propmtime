from PyQt5.QtWidgets import QLabel, QDialogButtonBox, QGridLayout, QDialog, QCheckBox

from balsa import get_logger
from tobool import to_bool_strict

from propmtime import __application_name__
from propmtime.gui import get_propmtime_preferences


"""
Displays a dialog box with the basic preferences and allows preferences to be changed.
"""

log = get_logger(__application_name__)


class PreferencesDialog(QDialog):
    def __init__(self):

        super().__init__()

        preferences_layout = QGridLayout()

        preferences_layout.addWidget(QLabel("Process Hidden Files/Folders"), 0, 0)
        self.hidden_checkbox = QCheckBox()
        preferences_layout.addWidget(self.hidden_checkbox, 0, 1)

        preferences_layout.addWidget(QLabel("Process System Files/Folders"), 1, 0)
        self.system_checkbox = QCheckBox()
        preferences_layout.addWidget(self.system_checkbox, 1, 1)

        preferences_layout.addWidget(QLabel('Process "dot" Files and Folders as Normal (instead of as System)'), 2, 0)
        self.process_dot_as_normal_checkbox = QCheckBox()
        preferences_layout.addWidget(self.process_dot_as_normal_checkbox, 2, 1)

        preferences_layout.addWidget(QLabel("Verbose"), 3, 0)
        self.verbose_checkbox = QCheckBox()
        preferences_layout.addWidget(self.verbose_checkbox, 3, 1)

        ok_button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_button_box.accepted.connect(self.ok)
        cancel_button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        cancel_button_box.rejected.connect(self.cancel)

        preferences_layout.addWidget(ok_button_box)  # , alignment=QtCore.Qt.AlignLeft)
        preferences_layout.addWidget(cancel_button_box)  # , alignment=QtCore.Qt.AlignLeft)

        pref = get_propmtime_preferences()
        self.hidden_checkbox.setChecked(to_bool_strict(pref.process_hidden))
        self.system_checkbox.setChecked(to_bool_strict(pref.process_system))
        self.process_dot_as_normal_checkbox.setChecked(to_bool_strict(pref.process_dot_as_normal))
        self.verbose_checkbox.setChecked(to_bool_strict(pref.verbose))

        self.setLayout(preferences_layout)

        self.setWindowTitle("Preferences")

    def ok(self):
        pref = get_propmtime_preferences()

        if self.hidden_checkbox.isChecked() != pref.process_hidden:
            pref.process_hidden = self.hidden_checkbox.isChecked()
        if self.system_checkbox.isChecked() != pref.process_system:
            pref.process_system = self.system_checkbox.isChecked()
        if self.process_dot_as_normal_checkbox.isChecked() != pref.process_dot_as_normal:
            pref.process_dot_as_normal = self.process_dot_as_normal_checkbox.isChecked()
        if self.verbose_checkbox.isChecked() != pref.verbose:
            pref.verbose = self.verbose_checkbox.isChecked()
        self.close()

    def cancel(self):
        self.close()
