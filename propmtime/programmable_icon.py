
from functools import lru_cache

from PyQt5.QtGui import QIcon, QPixmap, QColor

# this is needed for there to be an icon
from propmtime import icons


@lru_cache()
def get_icon(invert):

    # https://stackoverflow.com/questions/13350631/simple-color-fill-qicons-in-qt
    pixmap = QPixmap(':icon.png')

    if invert:
        mask = pixmap.mask()
        pixmap.fill((QColor('white')))
        pixmap.setMask(mask)

    icon = QIcon(pixmap)

    return icon

