
import os
import time
import temp.timestamp


def timestamp():
    write_timestamp()
    return temp.timestamp.timestamp


def get_temp_folder():
    temp_dir = 'temp'
    try:
        os.mkdir(temp_dir)
    except OSError:
        # already exists
        pass
    return temp_dir


def write_timestamp():
    with open(os.path.join(get_temp_folder(), '__init__.py'), 'w') as f:
        f.write('\n')
    with open(os.path.join(get_temp_folder(), 'timestamp.py'), 'w') as f:
        f.write('timestamp = "%s"\n' % time.strftime("%c"))

