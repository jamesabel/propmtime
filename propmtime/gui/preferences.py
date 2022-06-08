from attr import attrib, attrs
from pref import Pref, PrefOrderedSet

from propmtime import __application_name__, __author__


@attrs
class PropMTimePreferences(Pref):
    process_hidden: bool = attrib(default=None)
    process_system: bool = attrib(default=None)
    process_dot_as_normal: bool = attrib(default=False)
    verbose: bool = attrib(default=False)


def get_propmtime_preferences() -> PropMTimePreferences:
    return PropMTimePreferences(__application_name__, __author__)


def get_propmtime_paths() -> PrefOrderedSet:
    return PrefOrderedSet(__application_name__, __author__, "paths")


def get_propmtime_watched() -> PrefOrderedSet:
    return PrefOrderedSet(__application_name__, __author__, "watched")
