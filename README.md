# propmtime (propogate modification time) #
Author: James Abel

# tl;dr #
`propmtime` appropriately sets the modification time (mtime) of folders and directories to make finding recently created or changed files easier.

# Installation #

## Windows: ##

Download the [zip](https://github.com/jamesabel/propmtime/archive/master.zip) file and unzip it.

- Run `install_propmtime.exe` (in the `dist` folder).

and/or

- Copy `propmtime.exe` (in the `dist` folder) directly to your favorite utilities directory (usually something in the `PATH`).

## Linux: ##

Run from Python source directly.

    python propmtime/main.py

# Motivation #

The modification time (AKA mtime or modtime) of a folder/director and file is useful when you're trying to find something that has been recently modified.  For example, in a file explorer you can sort on "Date modified" so the most recently modified folders or files will be on top.

Unfortunately, there are some limitations to this method.  `propmtime` solves two common issues:

1. When you modify a file, the operating system only updates the mtime of the folder that directly contains the file that is changed.  The mtime of folders that are 'higher up' are not modified.  Therefore if you have several folder levels the highest parent folder will *not* have the mtime of the most recently modified file in its children.
2. Sometimes you want the mtime to reflect when a document was actually modified, not the file itself.  For example, when you scan in a file you may want the mtime to reflect when that document was done, not the scan time.  If you have a file name that reflects the date of the actual document, `propmtime` can find inconsistencies and (if you choose the -u option), it will update the mtime of the file.

# Description #

To address the issues given in the motivation, propmtime does two things:

1. Traverse a folder hierarchy (or 'tree') and assigns an mtime to a folder to the most recent mtime of the files or folders in that folder.  This way the folder mtime reflects the mtime of all of its children.
2. Looks for specific file name formats (conventions) and checks to see if the mtime of the file is the same as is the convention in the file name.  The default is to check for consistency, but the -u option can be used to have `propmtime` actually update the file's mtime.  These formats are:

	
	`YYYY_MM_DD_HH_MM_SS.<ext>`

	
	`<header>_M_D_Y.<ext>` where M and D can be 1 or 2 characters and Y can be 2 or 4 characters

	Examples:

	`2016_07_26_23_58_45.txt`  (July 26, 2016 at 11:58:34 PM)

	`somestring_7_26_16.txt`   (July 26, 2016)
	
# Usage #

The simplest use is to merely cd into a folder and run `propmtime`.  By default it will propagate all mtimes and also check file mtime consistency with the file name (if it has a conforming file name format).

Execute `propmtime -h` for help all options and usages.
