pushd .
cd ..
pushd .
cd ..\pyship
call build.bat
popd
call venv\Scripts\activate.bat
python -m pip uninstall -y pyship
python -m pip install -U pyship --no-index -f ..\pyship\dist
popd
deactivate
