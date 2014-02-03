
import argparse
import os
import propmtime.propmtime

if __name__ == "__main__":
    desc = """Many OSs (including Windows) only change the modification time of a folder/directory based on its
immediate children.  This code analyzes a folder and all of its children, and propagates (changes) the
modification times of each folder to be the most recent time of all of its children."""
    epi = [
'Examples:',
'propmtime.py -p documents          # process all normal files in the "documents" folder',
'propmtime.py -p documents -a h s   # process hidden and system files as well as normal files',
'propmtime.py -p documents -a s -v  # process system files as well as normal files, and turn on verbose'
]
    parser = argparse.ArgumentParser(epilog=epi)
    parser.add_argument('-v', '--verbose', action='store_true', default = False)
    parser.add_argument("-p", "--path", help="path to folder or directory")
    parser.add_argument("-a", "--attrib", nargs = "+", default = (''),
                        help="""ATTRIB can be h(idden) and/or s(ystem)to process hidden and/or system files.
Default is to ignore hidden and system files."""
    )
    args = parser.parse_args()

    process_hidden = False
    process_system = False
    for a in args.attrib:
        a = a.lower()
        a = a[0]
        if a == "h":
            process_hidden = True
        elif a == 's':
            process_system = True

    pmt = propmtime.propmtime.Propmtime(args.path, process_hidden, process_system, args.verbose)

    if args.path is not None:
        if not os.path.isdir(propmtime.util.get_long_abs_path(args.path)):
            print(("error:", args.path, "is not a folder/directory"))
            print ("exiting...")
            exit()
    if args.verbose:
        print(("path:", args.path))

    pmt.run()
    if args.verbose:
        pmt.print_stats()

