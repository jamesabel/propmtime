attrib -r build\*.* /s
rmdir /S /Q dist
rmdir /S /Q build
rmdir /S /Q propmtime.egg-info
call venv\Scripts\activate.bat
python setup.py bdist_wheel
deactivate
attrib -r build\*.* /s
rmdir /S /Q build
rmdir /S /Q propmtime.egg-info
