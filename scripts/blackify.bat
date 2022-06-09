pushd .
cd ..
call venv\Scripts\activate.bat
python -m black -l 192 propmtime test_propmtime setup.py
call deactivate
popd
