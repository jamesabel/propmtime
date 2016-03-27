import distutils
import py2exe
from propmtime import write_timestamp
from propmtime import build

write_timestamp.write_timestamp()

distutils.core.setup(
    console=['main.py'],

    name="propmtime",
    version=build.timestamp,
    author='James Abel',
    author_email='j@abel.co',
    url='www.lat.us',
    license='LICENSE', # points to the actual file
    description="propagate mtime to parent folders/directories",

    # make a single executable
    options={'py2exe': {'bundle_files': 1, 'compressed': True, }},

    zipfile = None,
)

