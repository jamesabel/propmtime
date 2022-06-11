from pathlib import Path

from PyQt5.QtGui import QFontMetrics, QFont
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QSystemTrayIcon, QMenu, QDialog, QApplication

from balsa import get_logger
from tobool import to_bool_strict


from propmtime import __application_name__, __version__, __url__, request_exit_via_event, is_windows
from propmtime import init_exit_control_event, TIMEOUT, PropMTime
from propmtime.gui import get_propmtime_paths, get_propmtime_preferences, PreferencesDialog, PropMTimeWatcher
from propmtime.gui import get_icon, PathsDialog, ScanDialog

log = get_logger(__application_name__)


class About(QDialog):
    def __init__(self, log_file_path):
        super().__init__()  # todo: fill in parameter?
        self.setWindowTitle(__application_name__)
        layout = QGridLayout(self)
        self.setLayout(layout)
        self.add_line("Version:", __version__, 1, layout)
        self.add_line("Source:", __url__, 3, layout)
        self.add_line("Logs:", log_file_path, 5, layout)
        self.show()

    def add_line(self, label, value, row_number, layout):
        value = str(value)
        layout.addWidget(QLabel(label), row_number, 0)
        log_dir_widget = QLineEdit(value)
        log_dir_widget.setReadOnly(True)
        width = QFontMetrics(QFont()).width(value) * 1.05
        log_dir_widget.setMinimumWidth(int(round(width)))
        layout.addWidget(log_dir_widget, row_number + 1, 0)


class PropMTimeSystemTray(QSystemTrayIcon):

    update_tool_tip_signal = pyqtSignal(str)  # pass in every file and directory that's looked at (as a string)

    def __init__(self, app, log_file_path: Path, parent=None):

        super().__init__(get_icon(False), parent)

        self.update_tool_tip_signal.connect(self.update_tool_tip)

        self.app = app
        self.log_file_path = log_file_path
        self.dir_and_file_counter = 0
        self.prior_invert_state = is_windows()

        menu = QMenu(parent)
        menu.addAction("Scan").triggered.connect(self.scan)
        menu.addAction("Scan All").triggered.connect(self.scan_all)
        menu.addAction("Stop Scan").triggered.connect(self.stop_scan)
        menu.addAction("Set Paths").triggered.connect(self.set_paths)
        menu.addAction("Preferences").triggered.connect(self.preferences)
        menu.addAction("About").triggered.connect(self.about)
        menu.addAction("Exit").triggered.connect(self.exit)
        self.setContextMenu(menu)

        self._watcher = PropMTimeWatcher(self.update_tool_tip_signal.emit)

        self._scanners = []

        self.update_tool_tip("")  # ready

    def update_tool_tip(self, path: str):
        """
        Call for every path that's looked at. Pass in an empty string to turn off the blinking.
        :param path: path of each folder or directory that's looked at
        """
        self.dir_and_file_counter += 1
        if len(path) > 0:
            self.setToolTip(f"Running ({self.dir_and_file_counter})")
            # only update the icon every so often (it still blinks fast enough this way)
            if self.dir_and_file_counter % 10 == 0:
                invert_icon = to_bool_strict(len(path) % 2)  # assume path lengths are split 50/50 odd vs even
                if self.prior_invert_state != invert_icon:
                    # avoid calling setIcon if the state hasn't changed
                    self.setIcon(get_icon(invert_icon))
                    self.prior_invert_state = invert_icon
        else:
            self.setToolTip("Ready")
            self.setIcon(get_icon(is_windows()))  # Windows icon is white, MacOS is black

    def scan_all(self):
        self.dir_and_file_counter = 0
        self.stop_scan()  # if any scans are running, stop them first
        pref = get_propmtime_preferences()
        for path in get_propmtime_paths().get():
            self.scan_one(Path(path), pref.process_hidden, pref.process_system, pref.process_dot_as_normal)

    def scan(self):
        scan_dialog = ScanDialog(self)
        scan_dialog.exec_()

    def scan_one(self, path: Path, do_hidden: bool, do_system: bool, process_dot_as_normal: bool):
        self.dir_and_file_counter = 0
        log.debug(f"scan_one : {path,do_hidden,do_system}")
        scanner = PropMTime(path, True, do_hidden, do_system, process_dot_as_normal, self.update_tool_tip_signal.emit)
        scanner.start()
        log.debug(f"scan started : {path}")
        self._scanners.append(scanner)

    def stop_scan(self):
        request_exit_via_event()  # tell all current scans to stop (if any)
        self.join_scans()  # wait for them to stop
        init_exit_control_event()  # re-init the exit control we just set
        self.update_tool_tip_signal.emit("")  # put icon back to normal

    def set_paths(self):
        paths_dialog = PathsDialog()
        paths_dialog.exec_()

    def join_scans(self):
        # join scans in process
        log.debug(f"waiting for {len(self._scanners)} scan threads")
        for scanner in self._scanners:
            scanner.join(TIMEOUT)
        for scanner in self._scanners:
            if scanner.is_alive():
                log.warning("could not stop : %s" % str(scanner))
        log.debug("all scan threads have been joined")
        self._scanners = []  # all existing scan threads have finished

    def preferences(self):
        # don't change things in the middle of a scan
        request_exit_via_event()
        self.join_scans()
        preferences_dialog = PreferencesDialog()
        preferences_dialog.exec_()
        # todo: update log verbosity (when balsa adds that capability)
        init_exit_control_event()

    def about(self):
        about_box = About(self.log_file_path)
        about_box.exec()

    def exit(self):
        log.info("exit")
        self.stop_scan()  # stop any scans currently underway
        if self._watcher:
            self._watcher.request_exit()
        self.hide()
        QApplication.exit()  # todo: what should this parameter be?
