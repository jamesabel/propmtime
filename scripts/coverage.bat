pushd .
cd ..
set PYTHONPATH=%CD%
mkdir cov
call venv\Scripts\activate.bat
python -m pytest --cov --cov-report=html
call deactivate
set PYTHONPATH=
popd
