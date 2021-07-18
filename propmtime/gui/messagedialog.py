# This pops up a dialog box in a separate process.  This is to work around a PyQt limitation that
# dialog boxes can not be created in threads that are not the main thread of an application.
# Perhaps eventually I'll create some sort of communication to the main thread, but this is easier for now.

# usage:
# cmd = '%s -c "%s" "%s"' % (sys.executable,  propmtime.messagedialog.program, msg)
# subprocess.check_call(cmd, shell=True)

program = r"""
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

app = QApplication([])
mb = QMessageBox()
mb.setWindowTitle('propmtime error')
mb.setText(sys.argv[1])
mb.show()
app.exec()
"""

if __name__ == "__main__":
    exec(program)
