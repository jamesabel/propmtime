import os
from setuptools import setup, find_packages

from propmtime import __application_name__, __version__, __author__

license_file_name = 'LICENSE'
requirements = ["pyqt5", "sqlalchemy", "appdirs", "watchdog", "lxml", "pypiwin32", "balsa", "requests"]
APP = ['main.py']

setup(
    name=__application_name__,
    version=__version__,
    description="",
    long_description="",
    author=__author__,
    author_email='j@abel.co',
    install_requires=requirements,
    packages=find_packages(),
    package_data={__application_name__: [license_file_name, os.path.join(__application_name__, license_file_name)]},

    app=APP,
    data_files=[],
    options={'py2app': {}},
    setup_requires=requirements,
)
