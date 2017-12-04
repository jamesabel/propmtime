
import threading

from propmtime import get_logger, __application_name__, Preferences, PropMTime, TIMEOUT

log = get_logger(__application_name__)


# todo: this can probably be refactored out in favor of other classes, or merge them into this class
class Scan(threading.Thread):

    def __init__(self, appdata_folder):
        super().__init__()
        self._appdata_folder = appdata_folder
        self.pmts = []
        self.exit_event = threading.Event()

    def run(self):
        log.info('starting scan')
        pref = Preferences(self._appdata_folder)
        for path in pref.get_all_paths():
            if not self.exit_event.is_set():
                pmt = PropMTime(path, True, pref.get_do_hidden(), pref.get_do_system())
                pmt.start()
                self.pmts.append(pmt)
                pmt.join(TIMEOUT)
                if pmt.is_alive():
                    log.warn('scan for "%s" did not complete before timeout' % path)
        log.info('scan complete')

    def request_exit(self):
        for pmt in self.pmts:
            pmt.request_exit()
        self.exit_event.set()
