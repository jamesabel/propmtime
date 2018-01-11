# propmtime (propagate file modification time) #
Author: James Abel

# Installers #

[propmtime windows installer](https://s3.amazonaws.com/abel.co/propmtime/propmtime_installer.exe)


# Summary #

`propmtime` sets the modification time (mtime) of folders/directories to make finding recently 
created or changed files easier.

Most OSs only change the modification time of a folder/directory based on its
immediate children.  This code analyzes a folder and its children, propagating (changing) the
modification times of each folder to be the most recent time of all of its children.

