import os
import datetime
from typing import Dict

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import sqlalchemy.exc

from balsa import get_logger
from tobool import to_bool
from typeguard import typechecked

from propmtime import __application_name__, __version__, DB_EXTENSION

log = get_logger(__application_name__)

"""
Reads/writes to the preferences DB.  All accesses to the DB are via this module.
"""


Base = sqlalchemy.ext.declarative.declarative_base()

PREFERENCES_FILE = "preferences" + DB_EXTENSION


class KeyValueTable(Base):
    __tablename__ = "keyvalue"

    key = sqlalchemy.Column(sqlalchemy.String(), primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.String())
    datetime = sqlalchemy.Column(sqlalchemy.DateTime())


class PathsTable(Base):
    __tablename__ = "paths"

    path = sqlalchemy.Column(sqlalchemy.String(), primary_key=True)
    watched = sqlalchemy.Column(sqlalchemy.Boolean())
    datetime = sqlalchemy.Column(sqlalchemy.DateTime())


class PropMTimePreferences:

    @typechecked()
    def __init__(self, app_data_folder: str, init=False):

        log.debug("Preferences __init__")

        self._do_hidden_string = "hidden"
        self._do_system_string = "system"
        self._process_dot_as_normal_string = "dot_as_normal"
        self._verbose_string = "verbose"
        self._background_monitor_string = "monitor"
        self._version_string = "version"  # this DB (not the overall app)

        self.version = "0.0.2"  # current version of the DB

        created_db = False

        if not app_data_folder:
            log.error(app_data_folder)
            raise RuntimeError

        self.app_data_folder = app_data_folder
        os.makedirs(self.app_data_folder, exist_ok=True)
        self._db_path = os.path.abspath(os.path.join(self.app_data_folder, PREFERENCES_FILE))
        self._sqlite_path = "sqlite:///" + self._db_path
        log.debug("preferences DB path : %s" % self._sqlite_path)
        self._db_engine = sqlalchemy.create_engine(self._sqlite_path)  # , echo=True)

        if init and Base.metadata.tables is None:
            # new DB
            log.info("creating DB")
            Base.metadata.create_all(self._db_engine)
            created_db = True

        # got an old version of the DB - initialize
        if init and not created_db and self.get_version() != self.version:
            log.warn("preferences DB - current version %s is incompatible with existing version %s - re-initializing" % (self.version, self.get_version()))
            Base.metadata.drop_all(self._db_engine)
            Base.metadata.create_all(self._db_engine)
            created_db = True

        if created_db:
            self.set_version(self.version)

        log.debug("exiting Preferences __init__")

    def get_db_path(self):
        return self._sqlite_path

    def _get_session(self):
        return sqlalchemy.orm.sessionmaker(bind=self._db_engine)()

    def _kv_set(self, key, value):
        log.debug("pref_set : %s to %s" % (str(key), str(value)))
        session = self._get_session()
        kv_table = KeyValueTable(key=key, value=value, datetime=datetime.datetime.utcnow())
        q = session.query(KeyValueTable).filter_by(key=key).first()
        if q:
            session.delete(q)
        session.add(kv_table)
        session.commit()
        session.close()
        log.debug("exiting pref_set")

    def _kv_get(self, key, default = None):
        value = None
        session = self._get_session()
        try:
            row = session.query(KeyValueTable).filter_by(key=key).first()
        except sqlalchemy.exc.OperationalError as e:
            row = None
        if row:
            value = row.value
        session.close()
        log.debug("pref_get : %s = %s" % (str(key), str(value)))
        if value is None:
            value = default
        return value

    @typechecked()
    def set_version(self, value: str):
        self._kv_set(self._version_string, value)

    @typechecked()
    def get_version(self) -> str:
        return self._kv_get(self._version_string)

    @typechecked()
    def set_do_hidden(self, value: bool):
        assert type(value) is bool
        self._kv_set(self._do_hidden_string, value)

    @typechecked()
    def get_do_hidden(self) -> bool:
        return to_bool(self._kv_get(self._do_hidden_string, False))

    @typechecked()
    def set_do_system(self, value: bool):
        assert type(value) is bool
        self._kv_set(self._do_system_string, to_bool(value))

    @typechecked()
    def get_do_system(self) -> bool:
        return to_bool(self._kv_get(self._do_system_string, False))

    @typechecked()
    def set_process_dot_as_normal(self, value: bool):
        assert type(value) is bool
        self._kv_set(self._process_dot_as_normal_string, to_bool(value))

    @typechecked()
    def get_process_dot_as_normal(self) -> bool:
        return to_bool(self._kv_get(self._process_dot_as_normal_string, False))

    @typechecked()
    def set_verbose(self, value: bool):
        assert type(value) is bool
        self._kv_set(self._verbose_string, value)

    @typechecked()
    def get_verbose(self) -> bool:
        return to_bool(self._kv_get(self._verbose_string, False))

    # Paths are stored in preferences as str, but the users of these methods generally have the paths as pathlib.Path. So, the user of this API is responsible
    # for "casting" the path from a pathlib.Path to a str before using these routines.

    @typechecked()
    def add_path(self, path: str):
        session = self._get_session()
        session.add(PathsTable(path=path, watched=False, datetime=datetime.datetime.utcnow()))
        session.commit()
        session.close()

    @typechecked()
    def remove_path(self, path: str):
        session = self._get_session()
        session.query(PathsTable).filter_by(path=path).delete()
        session.commit()
        session.close()

    @typechecked()
    def get_all_paths(self) -> Dict[str, bool]:
        session = self._get_session()
        paths = {row.path: row.watched for row in session.query(PathsTable)}
        session.close()
        for path in paths:
            log.debug("get_all_paths : %s" % path)
        return paths

    @typechecked()
    def set_path_watched(self, path: str, watched_value: bool):
        session = self._get_session()
        session.query(PathsTable).filter_by(path=path).update({"watched": watched_value})
        session.commit()
        session.close()

    @typechecked()
    def is_path_watched(self, path: str):
        session = self._get_session()
        watched = [row.watched for row in session.query(PathsTable).filter_by(path=path)]
        if watched and len(watched) > 0:
            # should only be one since only one row per path
            return to_bool(watched[0])
        return False

    def get_app_data_folder(self):
        return self.app_data_folder


def init_preferences_db(app_data_folder):
    # call this at the beginning of every program that uses this module
    pref = PropMTimePreferences(app_data_folder, init=True)
    log.info("%s version %s" % (__application_name__, __version__))
    log.info("preferences DB version %s" % pref.get_version())
