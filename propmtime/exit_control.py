# exit request spans both the CLI and the GUI

import threading

from pressenter2exit import PressEnter2Exit

from balsa import get_logger

from propmtime import __application_name__

g_exit_control_cli = None
g_exit_control_event = None  # can be used for GUI

log = get_logger(__application_name__)


def init_exit_control_cli():
    global g_exit_control_cli
    # ensure nothing has already been initialized
    assert g_exit_control_event is None
    assert g_exit_control_cli is None
    g_exit_control_cli = PressEnter2Exit(post_message="enter pressed - will now exit", pre_message="press enter to interrupt propmtime")


def is_exit_requested():
    # propmtime needs a single test for exit requested (i.e. that spans CLI and GUI)
    if g_exit_control_cli is not None:
        assert isinstance(g_exit_control_cli, threading.Thread)
        return not g_exit_control_cli.is_alive()
    if g_exit_control_event is not None:
        assert isinstance(g_exit_control_event, threading.Event)
        return g_exit_control_event.is_set()
    return False


def request_exit_via_event():
    # CLI doesn't need an exit request (pressenter2exit doesn't have or need an 'exit request' - this is taken care
    # of by the user pressing Enter).
    global g_exit_control_event
    assert isinstance(g_exit_control_event, threading.Event)
    g_exit_control_event.set()


def init_exit_control_event():
    global g_exit_control_event
    g_exit_control_event = threading.Event()
