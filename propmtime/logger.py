
import os
import sys
import appdirs
import logging
import logging.handlers
import subprocess
import shutil

import propmtime.util
import propmtime.gui
import propmtime.messagedialog


LOGGER_NAME_BASE = 'propmtime'
LOG_FILE_NAME = LOGGER_NAME_BASE + '.log'

log = None  # code that uses this module uses this logger

g_fh = None  # file handler
g_ch = None  # console handler
g_dh = None  # dialog handler
g_hh = None  # HTTP (log server) handler
g_appdata_folder = None
g_base_log_file_path = None  # 'base' since the file rotator can create files based on this file name

g_formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(lineno)s - %(funcName)s - %(levelname)s - %(message)s')


class DialogBoxHandlerAndExit(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        args = [sys.executable, '-c', propmtime.messagedialog.program, msg]
        print(str(args))
        subprocess.check_call(args)


def init_from_args(args):
    if args.appdatafolder:
        set_appdata_folder(args.appdatafolder)
    if args.test:
        init(backup_count=0)
    else:
        init()
    if args.test:
        # test is the more verbose mode
        set_console_log_level(logging.WARN)
        set_file_log_level(logging.DEBUG)
    elif args.verbose:
        set_console_log_level(logging.WARN)
        set_file_log_level(logging.INFO)


def init(log_folder=None, delete_existing_log_files=False, backup_count=3):
    global g_fh, g_ch, g_dh, log, g_base_log_file_path, g_appdata_folder

    if not log_folder:
        log_folder = appdirs.user_log_dir(propmtime.__author__, propmtime.__application_name__)

    logger_name = LOGGER_NAME_BASE
    log = logging.getLogger(logger_name)
    
    log.setLevel(logging.DEBUG)

    if delete_existing_log_files:
        shutil.rmtree(log_folder, ignore_errors=True)
    os.makedirs(log_folder, exist_ok=True)
    # create file handler
    g_base_log_file_path = os.path.join(log_folder, LOG_FILE_NAME)
    if backup_count > 0:
        max_bytes = 100*1E6  # normal usage
    else:
        max_bytes = 0  # no limit - used during testing
    g_fh = logging.handlers.RotatingFileHandler(g_base_log_file_path, maxBytes=max_bytes, backupCount=backup_count)
    g_fh.setFormatter(g_formatter)
    # see fh.setLevel() below for final level - we set this so we can put the log file path in the log file itself
    g_fh.setLevel(logging.INFO)
    log.addHandler(g_fh)

    # create console handler
    g_ch = logging.StreamHandler()
    g_ch.setFormatter(g_formatter)
    # see ch.setLevel() below for final level - we set this so we can display the log file path on the screen for debug
    g_ch.setLevel(logging.INFO)
    log.addHandler(g_ch)

    # create dialog box handler
    g_dh = DialogBoxHandlerAndExit()
    g_dh.setLevel(logging.FATAL)  # only pop this up as we're on the way out
    log.addHandler(g_dh)

    log.info('log_folder : %s' % os.path.abspath(log_folder))

    # real defaults
    set_console_log_level(logging.ERROR)
    # set the file log level last so we'll see the set of the console level in the log file
    set_file_log_level(logging.WARN)

    return log_folder


def set_file_log_level(new_level):
    if g_fh:
        # log the new level twice so we will likely see one of them, regardless if it's going up or down
        log.info('setting file logging to %s' % logging.getLevelName(new_level))
        g_fh.setLevel(new_level)
        log.info('setting file logging to %s' % logging.getLevelName(new_level))


def set_console_log_level(new_level):
    if g_ch:
        # log the new level twice so we will likely see one of them, regardless if it's going up or down
        log.info('setting console logging to %s' % logging.getLevelName(new_level))
        g_ch.setLevel(new_level)
        log.info('setting console logging to %s' % logging.getLevelName(new_level))


def set_appdata_folder(appdata_folder):
    global g_appdata_folder
    g_appdata_folder = appdata_folder


def get_base_log_file_path():
    global g_base_log_file_path
    return g_base_log_file_path

