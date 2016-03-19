
import time
import os


def write_timestamp():
    ts = time.strftime("%c")
    with open(os.path.join('propmtime', 'build.py'), 'w') as f:
        f.write('timestamp = "%s"\n' % ts)
    return ts
