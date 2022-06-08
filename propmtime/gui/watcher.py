import os
from pathlib import Path
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from balsa import get_logger

from propmtime import TIMEOUT, propmtime_event, __application_name__
from propmtime.gui import get_propmtime_paths, get_propmtime_watched, get_propmtime_preferences

log = get_logger(__application_name__)


class ModHandler(FileSystemEventHandler):
    def __init__(self, path: Path, running_callback: Callable):
        super().__init__()
        self._pmt_path = path
        self._running_callback = running_callback

    def on_any_event(self, event):
        super().on_any_event(event)
        log.debug("on_any_event : %s" % event)
        pref = get_propmtime_preferences()
        if not event.is_directory:
            propmtime_event(self._pmt_path, event.src_path, True, pref.process_hidden, pref.process_system, pref.process_dot_as_normal, self._running_callback)


class PropMTimeWatcher:
    def __init__(self, running_callback: Callable):
        self._running_callback = running_callback
        self._observer = Observer()
        self.schedule()

    def schedule(self):
        pref_paths = get_propmtime_paths().get()
        pref_watched = get_propmtime_watched().get()
        self._observer.unschedule_all()
        for path in pref_paths:
            if path in pref_watched:
                if os.path.exists(path):
                    event_handler = ModHandler(Path(path), self._running_callback)
                    log.info("scheduling watcher : %s" % path)
                    self._observer.schedule(event_handler, path=path, recursive=True)
                else:
                    log.error('Error: "%s" does not exist.\n\nPlease edit the path.\n\nTo do this, click on the %s icon and select "Paths".' % (path, __application_name__))
        self._observer.start()

    def request_exit(self):
        self._observer.unschedule_all()
        self._observer.stop()
        self._observer.join(TIMEOUT)
        try:
            if self._observer.isAlive():
                log.error("observer still alive")
        except AttributeError as e:
            log.info(e)  # for some reason the observer's attributes can disappear
