from PyQt5.QtWidgets import QLabel, QDialogButtonBox, QGridLayout, QDialog, QCheckBox
from PyQt5.QtCore import Qt

from propmtime import __application_name__, get_logger, PropMTimePreferences
import propmtime.gui.preferences


"""
Displays a dialog box with the basic preferences and allows preferences to be changed.
"""

log = get_logger(__application_name__)


class PreferencesDialog(QDialog):
    def __init__(self, app_data_folder):
        propmtime.logger.log.debug('preferences folder : %s' % app_data_folder)

        pref = PropMTimePreferences(app_data_folder)

        super().__init__()

        preferences_layout = QGridLayout()
        headers = ['Option', 'Enabled']
        col = 0
        for header in headers:
            preferences_layout.addWidget(QLabel(header), 0, col)
            col += 1
        row = 1
        self.selections = []
        self.selections.append({'str': 'Process Hidden Files/Folders', 'set': pref.set_do_hidden, 'get': pref.get_do_hidden})
        self.selections.append({'str': 'Process System Files/Folders', 'set': pref.set_do_system, 'get': pref.get_do_system})
        self.selections.append({'str': 'Verbose', 'set': pref.set_verbose, 'get': pref.get_verbose})
        for ss in self.selections:
            preferences_layout.addWidget(QLabel(ss['str']), row, 0)
            ss['cb'] = QCheckBox()
            if ss['get']():
                ss['cb'].setCheckState(Qt.Checked)
            preferences_layout.addWidget(ss['cb'], row, 1)
            row += 1

        ok_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_buttonBox.accepted.connect(self.ok)
        cancel_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
        cancel_buttonBox.rejected.connect(self.cancel)

        preferences_layout.addWidget(ok_buttonBox)     # , alignment=QtCore.Qt.AlignLeft)
        preferences_layout.addWidget(cancel_buttonBox) # , alignment=QtCore.Qt.AlignLeft)

        self.setLayout(preferences_layout)

        self.setWindowTitle("Preferences")

    def ok(self):
        for selection in self.selections:
            if selection['cb'].isChecked() != selection['get']():
                propmtime.logger.log.info('new preferences for %s : %s --> %s' % (selection['str'], str(selection['get']()), str(selection['cb'].isChecked())))
                selection['set'](selection['cb'].isChecked())
        self.close()

    def cancel(self):
        self.close()
