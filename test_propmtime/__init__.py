from pathlib import Path

application_name = "test_propmtime"
data_parent = Path("test_propmtime", "data", "parent")
child_folder = Path(data_parent, "child")
time_offset_sec = 10.0 * 60.0

from .os_util import mkdirs, rmdir
