#!/usr/bin/env bash
pushd .
cd ../osnap
../propmtime/venv/bin/python setup.py install
popd
