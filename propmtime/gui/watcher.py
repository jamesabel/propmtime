
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from balsa import get_logger

from propmtime import TIMEOUT, propmtime_event, __application_name__, PropMTimePreferences

log = get_logger(__application_name__)


class ModHandler(FileSystemEventHandler):
    def __init__(self, path, app_data_folder):
        super().__init__()
        self._pmt_path = path
        self._app_data_folder = app_data_folder

    def on_any_event(self, event):
        super().on_any_event(event)
        log.debug('on_any_event : %s' % event)
        pref = PropMTimePreferences(self._app_data_folder)
        if not event.is_directory:
            propmtime_event(self._pmt_path, event.src_path, True, pref.get_do_hidden(), pref.get_do_system())


class PropMTimeWatcher:
    def __init__(self, app_data_folder):
        self._app_data_folder = app_data_folder
        self._observer = Observer()
        self.schedule()

    def schedule(self):
        pref = PropMTimePreferences(self._app_data_folder)
        self._observer.unschedule_all()
        for path, watcher in pref.get_all_paths().items():
            if watcher:
                if os.path.exists(path):
                    event_handler = ModHandler(path, self._app_data_folder)
                    log.info('scheduling watcher : %s' % path)
                    self._observer.schedule(event_handler, path=path, recursive=True)
                else:
                    log.error('Error: "%s" does not exist.\n\nPlease edit the path.\n\nTo do this, click on the %s icon and select "Paths".' %
                              (path, __application_name__))
        self._observer.start()

    def request_exit(self):
        self._observer.unschedule_all()
        self._observer.stop()
        self._observer.join(TIMEOUT)
        if self._observer.isAlive():
            log.error('observer still alive')
