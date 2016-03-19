
import tempfile
import os
import shutil
import unittest
import win32api
import win32con
import time
import propmtime.propmtime
import propmtime.timestamp


class FileCreator():
    """
    file creator
    """
    def __init__(self, current_time, ldir, file_name, time_offset, attributes=win32con.FILE_ATTRIBUTE_NORMAL):
        self.dir = ldir
        os.makedirs(self.dir, exist_ok=True)
        self.full_path = os.path.join(self.dir, file_name)
        self.time_offset = time_offset
        self.current_time = current_time
        self.time_offset_unit = 24 * 60 * 60 # 1 day
        with open(self.full_path, "w") as f:
            f.write(os.path.abspath(self.full_path)) # just put something in the file ... this is as good as anything
        win32api.SetFileAttributes(self.full_path, attributes)
        self.mtime = self.current_time - (time_offset * self.time_offset_unit)
        os.utime(self.full_path, (self.mtime, self.mtime))

    def get_time_offset_unit(self):
        return self.time_offset_unit

    def get_time(self):
        return self.mtime


class TestPropmtime(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp()
        print("temp testing dir", self.root)
        self.child = os.path.join(self.root, 'temp2')
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        self.current_time = time.time() # one time base for all

        # make normal the earliest so we can test system and hidden
        self.system = FileCreator(self.current_time, self.child, 'system.txt', 1, win32con.FILE_ATTRIBUTE_SYSTEM)
        self.hidden = FileCreator(self.current_time, self.child, 'hidden.txt', 2, win32con.FILE_ATTRIBUTE_HIDDEN)
        self.normal = FileCreator(self.current_time, self.child, 'normal.txt', 3)

        # todo: have this not require some arbitrary instance line 'normal'
        self.root_dir_init_offset = 4
        folder_mtime = self.current_time - self.normal.get_time_offset_unit() * self.root_dir_init_offset
        os.utime(self.root, (folder_mtime, folder_mtime))

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_normal(self):
        pmt = propmtime.propmtime.Propmtime(self.root, print_flag=True)
        pmt.run()
        self.compare_times(os.path.getmtime(self.root), self.normal.get_time())

    def test_hidden(self):
        pmt = propmtime.propmtime.Propmtime(self.root, process_hidden=True, print_flag=True)
        pmt.run()
        self.compare_times(os.path.getmtime(self.root), self.hidden.get_time())

    def test_system(self):
        pmt = propmtime.propmtime.Propmtime(self.root, process_system=True, print_flag=True)
        pmt.run()
        self.compare_times(os.path.getmtime(self.root), self.system.get_time())

    def test_all(self):
        pmt = propmtime.propmtime.Propmtime(self.root, process_hidden=True, process_system=True, print_flag=True)
        pmt.run()
        self.compare_times(os.path.getmtime(self.root), self.system.get_time())

    def compare_times(self, t1, t2):
        scale = 10 # get within this # of sec
        t1 /= scale
        t2 /= scale
        self.assertAlmostEqual(t1, t2, places=1)

    def test_timestamp(self):
        ts = propmtime.timestamp.timestamp()

    def test_main(self):
        from main import main

        class ParsedArgs:
            verbose = True
            attrib = []
            path = '.'
        main(ParsedArgs())

if __name__ == "__main__":
    unittest.main()