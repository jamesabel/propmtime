
import appdirs

from PyQt5.QtWidgets import QLabel, QDialogButtonBox, QGridLayout, QDialog, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.Qt import QApplication

from propmtime import __application_name__, __author__, get_logger, init_propmtime_logger, get_arguments
import propmtime.preferences


"""
Displays a dialog box with the basic preferences and allows preferences to be changed.
"""

log = get_logger(__application_name__)


class PreferencesDialog(QDialog):
    def __init__(self, app_data_folder):
        propmtime.logger.log.info('starting PreferencesDialog')
        propmtime.logger.log.info('preferences folder : %s' % app_data_folder)

        preferences = propmtime.preferences.Preferences(app_data_folder, True)

        super().__init__()
        row = 1

        preferences_layout = QGridLayout()
        headers = ['Option', 'Enabled']
        col = 0
        for header in headers:
            preferences_layout.addWidget(QLabel(header), 0, col)
            col += 1
        row = 1
        self.selections = []
        self.selections.append({'str': 'Monitor Folders in the Background (unchecked: manual only)', 'set': preferences.set_background_monitor, 'get': preferences.get_background_monitor})
        self.selections.append({'str': 'Process Hidden Files/Folders', 'set': preferences.set_do_hidden, 'get': preferences.get_do_hidden})
        self.selections.append({'str': 'Process System Files/Folders', 'set': preferences.set_do_system, 'get': preferences.get_do_system})
        self.selections.append({'str': 'Verbose', 'set': preferences.set_verbose, 'get': preferences.get_verbose})
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
