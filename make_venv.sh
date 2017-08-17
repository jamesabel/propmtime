#!/usr/bin/env bash
python3 -m venv --clear venv
venv/bin/pip install -U pip
venv/bin/pip install -U setuptools
venv/bin/pip install -r requirements.txt
#
# testing tools - these can be ignored when creating the production release - i.e. the frozen executables
#venv/bin/pip install -U coverage
# pyautogui will not install properly from requirements.txt
#venv/bin/pip install -U pyobjc-core
#venv/bin/pip install -U pyobjc
#venv/bin/pip install -U pyautogui
#
# install the latest osnap from source
./install_osnap.sh
