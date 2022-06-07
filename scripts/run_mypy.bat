pushd .
cd ..
call venv\Scripts\activate.bat 
mypy -m propmtime
mypy -m test_propmtime
call deactivate
popd
