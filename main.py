
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

    pmt = propmtime.Propmtime(parsed_args.path, process_hidden, process_system, parsed_args.verbose)

    if parsed_args.path is not None:
        if not os.path.isdir(util.get_long_abs_path(parsed_args.path)):
            print(("error:", parsed_args.path, "is not a folder/directory"))
            print ("exiting...")
            exit()
    if parsed_args.verbose:
        print(("path:", parsed_args.path))

    pmt.run()
    if parsed_args.verbose:
        pmt.print_stats()

if __name__ == "__main__":
    desc = """Many OSs (including Windows) only change the modification time of a folder/directory based on its
immediate children.  This code analyzes a folder and all of its children, and propagates (changes) the
modification times of each folder to be the most recent time of all of its children."""
    epi = """
Examples:
propmtime -p documents          # process all normal files in the "documents" folder
propmtime -p documents -a h s   # process hidden and system files as well as normal files
propmtime -p documents -a s -v  # process system files as well as normal files, and turn on verbose
"""
    parser = argparse.ArgumentParser(epilog=epi, description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', default = False)
    parser.add_argument("-p", "--path", required=True, help="path to folder or directory")
    parser.add_argument("-a", "--attrib", nargs = "+", default = (''),
                        help="""ATTRIB can be h(idden) and/or s(ystem)to process hidden and/or system files.
Default is to ignore hidden and system files."""
    )
    main(parser.parse_args())
