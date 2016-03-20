
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

    file_mtime = propmtime.FileMTime.do_nothing
    if parsed_args.update:
        file_mtime = propmtime.FileMTime.update_mtime
    elif parsed_args.simulate:
        file_mtime = propmtime.FileMTime.show_differences
    pmt = propmtime.Propmtime(parsed_args.path, file_mtime, process_hidden, process_system, parsed_args.verbose)

    if parsed_args.path is not None:
        if not os.path.isdir(util.get_long_abs_path(parsed_args.path)):
            print(("error:", parsed_args.path, "is not a folder/directory"))
            print ("exiting...")
            exit()
    if parsed_args.verbose:
        print("path : %s" % parsed_args.path)
        print("file mtime directive : %s" % str(file_mtime))

    pmt.run()
    if parsed_args.verbose:
        pmt.print_stats()

if __name__ == "__main__":
    desc = """Many OSs (including Windows) only change the modification time of a folder/directory based on its immediate children.
This code analyzes a folder and all of its children, and propagates (changes) the modification times of each folder to
be the most recent time of all of its children.""" \
+ "\n\nbuild : " + build.timestamp
    epi = """
file mtime substring must follow the following convention:
- have a substring at the end of the main part of the file name (before the file extension) that is
  <month><delimiter><day><delimiter><year>.  A common delimiters is underscore (_), but it can also be whitespace characters.
- month is 1-12 (1=Jan, 2=Feb, etc.) or a string that uniquely identified the month.
- day is 1-31
- year is 2 or 4 digits.  If it's 2 digits, if they are greater than the current 2 digit year then the base is assumed
  to be 19xx.  If not the base is 20xx.

Examples:
propmtime -p documents          # process all normal files in the "documents" folder
propmtime -p documents -a h s   # process hidden and system files as well as normal files
propmtime -p documents -a s -v  # process system files as well as normal files, and turn on verbose
"""
    parser = argparse.ArgumentParser(epilog=epi, description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-u', '--update', action='store_true', default=False,
                        help='update the file mtime to a value derived from the file name with the pattern described below')
    parser.add_argument('-s', '--simulate', action='store_true', default=True,
                        help='only simulate the file mtime change and write the intent to stdout')
    parser.add_argument("-p", "--path", default=".", help="path to folder or directory")
    parser.add_argument("-a", "--attrib", nargs="+", default=(''),
                        help="""ATTRIB can be h(idden) and/or s(ystem)to process hidden and/or system files.
Default is to ignore hidden and system files."""
    )
    main(parser.parse_args())
