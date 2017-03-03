
import appdirs

import propmtime
import propmtime.gui


def main(app_data_folder):
    propmtime.gui.main(app_data_folder)

if __name__ == '__main__':
    main(appdirs.user_config_dir(appname=propmtime.__application_name__, appauthor=propmtime.__author__))
