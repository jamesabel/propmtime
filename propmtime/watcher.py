
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import propmtime
import propmtime.preferences
import propmtime.logger
import propmtime.const


class ModHandler(FileSystemEventHandler):
    def __init__(self, path, app_data_folder):
        super().__init__()
        self._pmt_path = path
        self._app_data_folder = app_data_folder

    def on_any_event(self, event):
        super().on_any_event(event)
        propmtime.logger.log.info('on_any_event : %s' % event)
        pref = propmtime.preferences.Preferences(self._app_data_folder)
        if not event.is_directory:
            propmtime.event(self._pmt_path, event.src_path, True, pref.get_do_hidden(), pref.get_do_system())


class Watcher:
    def __init__(self, app_data_folder):
        self._app_data_folder = app_data_folder
        self._observer = Observer()
        self.schedule()

    def schedule(self):
        pref = propmtime.preferences.Preferences(self._app_data_folder)
        self._observer.unschedule_all()
        for path in pref.get_all_paths():
            event_handler = ModHandler(path, self._app_data_folder)
            start_time = time.time()
            propmtime.logger.log.info('start scheduling watcher : %s' % path)
            self._observer.schedule(event_handler, path=path, recursive=True)
            propmtime.logger.log.info('watcher scheduled : %s (%f seconds)' % (path, time.time() - start_time))
        self._observer.start()

    def request_exit(self):
        self._observer.unschedule_all()
        self._observer.stop()
        self._observer.join(propmtime.const.TIMEOUT)
        if self._observer.isAlive():
            propmtime.logger.log.error('observer still alive')
