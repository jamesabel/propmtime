call make_dist.bat
pushd .
cd ..
call venv\Scripts\activate.bat
python -m pyship -p default
call deactivate
popd
