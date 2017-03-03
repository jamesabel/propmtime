# propmtime (propogate modification time) #
Author: James Abel

# Summary #
`propmtime` appropriately sets the modification time (mtime) of folders/directories to make finding recently created or changed files easier.

Most OSs only change the modification time of a folder/directory based on its
immediate children.  This code analyzes a folder and its children, propagating (changing) the
modification times of each folder to be the most recent time of all of its children

# Appendix/Notes #

py2app (\*_py2app.[sh|bat] files) is not working - use osnap (\*_osnap.[sh|bat] files).
