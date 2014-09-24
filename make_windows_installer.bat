REM for PyQt
REM mkdir dist\platforms
REM copy /Y C:\Python33\Lib\site-packages\PyQt5\plugins\platforms\*.dll dist\platforms
c:\python33\python.exe setup.py py2exe
"C:\Program Files (x86)\NSIS\makensis.exe" propmtime.nsi
