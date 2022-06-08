from pathlib import Path

from PyQt5.QtWidgets import QMessageBox

from propmtime import __application_name__
from propmtime.gui import PropMTimeSystemTray


def test_gui_preferences(qtbot):

    QMessageBox.information(None, __application_name__, "This is only semi-automated - human tester must click on the GUI windows as they appear. Cancel or OK is sufficient.")

    log_file_path = Path("log", "test_gui_preferences.log")  # just for display - doesn't actually write to this file
    propmtime_gui = PropMTimeSystemTray(qtbot, log_file_path)
    propmtime_gui.preferences()
    propmtime_gui.set_paths()
    propmtime_gui.scan()
    propmtime_gui.exit()
