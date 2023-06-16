pushd .
cd ..
rmdir /S /Q venv
"\Program Files\Python310\python.exe" -m venv --clear venv
venv\Scripts\python.exe -m pip install --no-deps --upgrade pip
venv\Scripts\pip.exe install -U setuptools
venv\Scripts\pip.exe install -U -r requirements-dev.txt
popd
