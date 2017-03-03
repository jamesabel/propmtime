
import time
import os

import propmtime
import propmtime.logger
import test_propmtime


def get_mtimes(root_folder, file_path):
    root_mtime = os.path.getmtime(root_folder)
    file_mtime = os.path.getmtime(file_path)
    propmtime.logger.log.info('%s mtime : %f' % (root_folder, root_mtime))
    propmtime.logger.log.info('%s mtime : %f' % (file_path, file_mtime))
    propmtime.logger.log.info('difference : %f seconds' % (root_mtime - file_mtime))
    return root_mtime, file_mtime


def run(is_hidden, is_system):
    current_time = time.time()
    file_name = 'myfile.txt'
    if propmtime.util.is_mac() and is_hidden:
        file_name = '.' + file_name
    file_path = os.path.join(test_propmtime.child_folder, file_name)
    test_propmtime.file_creator(current_time, file_path, 1, is_hidden, is_system)

    root_mtime, file_mtime = get_mtimes(test_propmtime.data_root, file_path)
    assert((root_mtime - file_mtime) >= (test_propmtime.time_offset_unit - test_propmtime.time_accuracy_window))

    pmt = propmtime.PropMTime(test_propmtime.data_root, True, is_hidden, is_system)
    pmt.start()
    pmt.join()

    root_mtime, file_mtime = get_mtimes(test_propmtime.data_root, file_path)
    assert(abs(root_mtime - file_mtime) < test_propmtime.time_accuracy_window)


def test_normal():
    run(False, False)


def test_hidden():
    run(True, False)


def test_system():
    run(False, True)


def test_both():
    run(True, True)
