from pathlib import Path
from datetime import datetime

from propmtime import PropMTime

from test_propmtime import data_root, mkdirs, create_zip, file_creator, check_mtime

test_name = "test_zip"


def test_zip():
    parent = Path(data_root, test_name)
    mkdirs(parent, remove_first=True)
    data_directory = Path(parent, "data")
    file_name = "a.txt"
    file_a_path = Path(data_directory, file_name)
    mtime = datetime(year=2020, month=2, day=3, hour=4, minute=5, second=6).timestamp()
    file_creator(file_a_path, mtime)
    zip_path = Path(parent, f"{data_directory.name}.zip")
    create_zip(data_directory, zip_path)

    prop_mtime = PropMTime(parent, True, False, False, False, print)
    prop_mtime.start()
    prop_mtime.join()

    check_mtime(parent, mtime)
    check_mtime(zip_path, mtime)
