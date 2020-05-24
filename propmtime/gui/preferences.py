import os
import datetime
from distutils.util import strtobool

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import sqlalchemy.exc

from balsa import get_logger

from propmtime import __application_name__, __version__, DB_EXTENSION, convert_to_bool

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
    def __init__(self, app_data_folder, init=False):

        log.debug("Preferences __init__")

        self._do_hidden_string = "hidden"
        self._do_system_string = "system"
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

    def _kv_get(self, key):
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
        return value

    def set_version(self, value):
        self._kv_set(self._version_string, value)

    def get_version(self):
        return self._kv_get(self._version_string)

    def set_do_hidden(self, value):
        assert type(value) is bool
        self._kv_set(self._do_hidden_string, value)

    def get_do_hidden(self):
        return convert_to_bool(self._kv_get(self._do_hidden_string))

    def set_do_system(self, value):
        assert type(value) is bool
        self._kv_set(self._do_system_string, convert_to_bool(value))

    def get_do_system(self):
        return convert_to_bool(self._kv_get(self._do_system_string))

    def set_verbose(self, value):
        assert type(value) is bool
        self._kv_set(self._verbose_string, value)

    def get_verbose(self):
        return convert_to_bool(self._kv_get(self._verbose_string))

    def add_path(self, path):
        session = self._get_session()
        session.add(PathsTable(path=path, watched=False, datetime=datetime.datetime.utcnow()))
        session.commit()
        session.close()

    def remove_path(self, path):
        session = self._get_session()
        session.query(PathsTable).filter_by(path=path).delete()
        session.commit()
        session.close()

    def get_all_paths(self):
        session = self._get_session()
        paths = {row.path: row.watched for row in session.query(PathsTable)}
        watches = [row.watched for row in session.query(PathsTable)]
        session.close()
        for path in paths:
            log.debug("get_all_paths : %s" % path)
        return paths

    def set_path_watched(self, path, watched_value):
        session = self._get_session()
        session.query(PathsTable).filter_by(path=path).update({"watched": watched_value})
        session.commit()
        session.close()

    def is_path_watched(self, path):
        session = self._get_session()
        watched = [row.watched for row in session.query(PathsTable).filter_by(path=path)]
        if watched and len(watched) > 0:
            # should only be one since only one row per path
            return convert_to_bool(watched[0])
        return False

    def get_app_data_folder(self):
        return self.app_data_folder


def init_preferences_db(app_data_folder):
    # call this at the beginning of every program that uses this module
    pref = PropMTimePreferences(app_data_folder, init=True)
    log.info("%s version %s" % (__application_name__, __version__))
    log.info("preferences DB version %s" % pref.get_version())
