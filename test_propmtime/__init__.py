
import os

data_root = os.path.join('test_propmtime', 'data')
child_folder = os.path.join(data_root, 'child')
time_accuracy_window = 2  # seconds
time_offset_unit = 24 * 60 * 60  # 1 day

from .file_creator import file_creator
