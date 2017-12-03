
import threading
import time

from propmtime import is_windows, get_icon, get_logger, __application_name__, TIMEOUT

_blinking = False  # blinking flag
_blink = None  # the one and only instance of Blink class

log = get_logger(__application_name__)


def set_blinking(value):
    """
    Turn blinking on or off.
    :param value: True to turn blinking on, False to turn it off
    """
    global _blinking
    _blinking = value
    if _blink:
        # in case we get called from the CLI version, don't 'start blinking'
        _blink.start_blinking()


def init_blink(sys_tray):
    global _blink
    if _blink is None:
        _blink = _Blink(sys_tray)
        _blink.start()
    else:
        log.error('blink already initialized')


def request_blink_exit():
    _blink.request_exit()
    _blink.join(TIMEOUT)


class _Blink(threading.Thread):
    def __init__(self, sys_tray):
        super().__init__()
        self.sys_tray = sys_tray
        self.icon_invert = is_windows()  # Windows icon is white, MacOS is black
        self.prior_icon = None

        self.timer = threading.Event()
        self.exit_flag = False

    def run(self):
        self.prior_icon = get_icon(self.icon_invert)
        while not self.exit_flag:

            # Usually we get a start_blinking way before this times out, but this is the blink period for really
            # long prop mtimes.
            self.timer.wait(1.0)

            if _blinking:
                self.icon_invert = not self.icon_invert
            else:
                self.icon_invert = is_windows()
            self.sys_tray.setIcon(get_icon(self.icon_invert))
            self.timer.set()
            self.timer = threading.Event()

    def start_blinking(self):
        self.timer.set()

    def request_exit(self):
        self.exit_flag = True
        self.timer.set()
