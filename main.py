
import appdirs

from propmtime import __application_name__, __author__
import propmtime.gui


def main(app_data_folder):
    propmtime.gui.main(app_data_folder)


if __name__ == '__main__':
    main(appdirs.user_config_dir(appname=__application_name__, appauthor=__author__))
