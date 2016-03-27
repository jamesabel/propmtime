
import argparse
import os
from propmtime import propmtime
from propmtime import util
from propmtime import build


def main(parsed_args):
    if parsed_args.verbose:
        print('build : %s' % build.timestamp)
    process_hidden = False
    process_system = False
    for a in parsed_args.attrib:
        a = a.lower()
        a = a[0]
        if a == "h":
            process_hidden = True
        elif a == 's':
            process_system = True

    pmt = propmtime.Propmtime(parsed_args.path, parsed_args.update, parsed_args.silent, process_hidden, process_system,
                              parsed_args.verbose)

    if parsed_args.path is not None:
        if not os.path.isdir(util.get_long_abs_path(parsed_args.path)):
            print(("error:", parsed_args.path, "is not a folder/directory"))
            print ("exiting...")
            exit()
    if parsed_args.verbose:
        print("path : %s" % parsed_args.path)
        print("update : %s" % parsed_args.update)
        print("silent : %s" % parsed_args.silent)

    pmt.run()
    if parsed_args.verbose:
        pmt.print_stats()

if __name__ == "__main__":
    desc = """Many OSs (including Windows) only change the modification time of a folder/directory based on its immediate children.
This code analyzes a folder and all of its children, and propagates (changes) the modification times of each folder to
be the most recent time of all of its children.""" \
+ "\n\nbuild : " + build.timestamp
    epi = """
file mtime examples:
 hi_there_1_2_16.txt  # year can be 2 or 4 digits
 Fri_Dec_28_21_22_21_2007.jpg
 2016_02_28_11_07_15.jpg
"""
    parser = argparse.ArgumentParser(epilog=epi, description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-u', '--update', action='store_true', default=False,
                        help='Update the file mtime to a value derived from the file name with the pattern described below. (default=False)')
    parser.add_argument('-s', '--silent', action='store_true', default=False,
                        help='Do not print messages when file mtimes do not match file name format.  Use when you only want folder mtime updates (not files). (default=False')
    parser.add_argument("-p", "--path", default=".", help='Path to folder or directory.  (default=".")')
    parser.add_argument("-a", "--attrib", nargs="+", default='',
                        help="""ATTRIB can be h(idden) and/or s(ystem)to process hidden and/or system files.
Default is to ignore hidden and system files."""
    )
    main(parser.parse_args())
