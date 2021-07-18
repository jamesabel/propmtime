venv\scripts\python.exe setup.py py2exe
REM hack
move dist\main.exe dist\propmtime.exe
"C:\Program Files (x86)\NSIS\makensis.exe" propmtime.nsi
