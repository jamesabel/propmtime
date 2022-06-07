from functools import lru_cache

from PyQt5.QtGui import QIcon, QPixmap, QColor

from balsa import get_logger

from propmtime import __application_name__

# this is needed for there to be an icon (NOTE: PyCharm will say this is unused ... IT ACTUALLY IS - DO NOT DELETE!!!)
from propmtime.gui import icons

log = get_logger(__application_name__)


@lru_cache()
def get_icon(invert: bool):

    # https://stackoverflow.com/questions/13350631/simple-color-fill-qicons-in-qt
    pixmap = QPixmap(":icon.png")
    assert pixmap is not None

    if invert:
        log.debug("inverting icon")
        mask = pixmap.mask()
        pixmap.fill((QColor("white")))
        pixmap.setMask(mask)

    icon = QIcon(pixmap)

    return icon
