call venv\Scripts\activate.bat
REM packages not in pypi (can not be installed with pip):
easy_install.exe third_party_installers\pywin32-219.win-amd64-py3.4.exe
REM
REM PySide not installing this way so use PySide-1.2.2.win-amd64-py3.4.exe
REM pip.exe install PySide
easy_install.exe third_party_installers\PySide-1.2.2-py3.4-win-amd64.egg