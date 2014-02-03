from cx_Freeze import setup, Executable

base = 'Console'

setup(  name='propmtime',
        description='propagate mtime to parent folders/directories',
        version='1.0',
        #packages=['propmtime'],
        url='http://github.com/latusrepo/propmtime',
        author='James Abel',
        author_email='j@abel.co',
        license='LICENSE',
        #py_modules=['*'],
        platforms=['windows'],
        executables = [Executable(script="propmtime.py",base=base)]
      )

