
import osnap.installer

import propmtime


def make_installer():
    osnap.installer.make_installer(propmtime.__python_version__, propmtime.__application_name__, propmtime.__author__,
                                   'propagate the modification time up the directory/folder tree',
                                   'https://github.com/jamesabel/propmtime')


if __name__ == '__main__':
    make_installer()
