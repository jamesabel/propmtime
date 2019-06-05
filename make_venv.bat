"C:\Program Files\Python37\python.exe" -m venv --clear venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip3 install -U setuptools
REM venv\Scripts\pip3 install -U --find-links ..\osnap\dist -r requirements.txt
venv\Scripts\pip3 install -U -r requirements.txt
