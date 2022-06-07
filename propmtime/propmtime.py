import os
import threading
import time
from typing import Callable, Union

from balsa import get_logger

from propmtime import __application_name__, is_mac, is_exit_requested, do_propagation


log = get_logger(__application_name__)


class PropMTime(threading.Thread):
    def __init__(self, root, update: bool, process_hidden: bool, process_system: bool, process_dot_as_normal: bool, running_callback: Union[Callable, None], set_blinking):
        self._root = root
        self._update = update
        self._process_hidden = process_hidden
        self._process_system = process_system
        self._process_dot_as_normal = process_dot_as_normal
        self._running_callback = running_callback
        self.set_blinking = set_blinking
        self.error_count = 0
        self.files_folders_count = 0
        self.total_time = None
        super().__init__()

    # scan and propagate the modification time of a folder/directory from its children (files or folders/directories)
    def run(self):

        start_time = time.time()

        log.debug(f"{self._root} : scan started")
        log.debug(f"{self._root} : {self._process_hidden=}")
        log.debug(f"{self._root} : {self._process_system=}")
        log.debug(f"{self._root} : {self._process_system=}")
        log.debug(f"{self._root} : {self._update=}")

        for walk_folder, dirs, files in os.walk(self._root, topdown=False):
            if is_exit_requested():
                break
            if walk_folder:
                # For Mac we have to explicitly check to see if this path is hidden.
                # For Windows this is taken care of with the hidden file attribute.
                if (is_mac() and (self._process_hidden or "/." not in walk_folder)) or not is_mac():
                    ffc, ec = do_propagation(walk_folder, dirs + files, start_time, self._update, self._process_hidden, self._process_system, self._process_dot_as_normal, self.set_blinking)
                    self.files_folders_count += ffc
                    self.error_count += ec
                else:
                    log.debug("skipping %s" % walk_folder)
            else:
                log.warn("no os.walk root")

        self.total_time = time.time() - start_time

        log.info(f"{self._root} : is_exit_requested : {is_exit_requested()}")
        log.info(f"{self._root} : file_folders_count : {self.files_folders_count}")
        log.info(f"{self._root} : error_count : {self.error_count}")
        log.info(f"{self._root} : total_time : {self.total_time} seconds")

        if self._running_callback is not None:
            self._running_callback(False)
