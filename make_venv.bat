"C:\Program Files\Python36\python.exe" -m venv --clear venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip3 install -U setuptools
venv\Scripts\pip3 install -U --find-links ..\osnap\dist -r requirements.txt
