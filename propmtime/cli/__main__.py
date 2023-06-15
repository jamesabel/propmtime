from balsa import Balsa

from propmtime import get_arguments, log_selections, init_exit_control_cli, __application_name__, __author__, PropMTime


def cli_main():
    args = get_arguments()

    balsa = Balsa(__application_name__, __author__)
    balsa.init_logger_from_args(args)

    log_selections(args)

    init_exit_control_cli()

    pmt = PropMTime(args.path, not args.noupdate, args.hidden, args.system, False, None)
    pmt.start()
    pmt.join()  # pmt uses exit control
    if not args.silent:
        print()
        print(f"processed {pmt.files_folders_count} files/folders in {pmt.total_time} seconds")


if __name__ == "__main__":
    cli_main()
