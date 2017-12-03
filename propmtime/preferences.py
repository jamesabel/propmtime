
import os
import datetime

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import sqlalchemy.exc

from propmtime import __application_name__, get_logger, DB_EXTENSION

log = get_logger(__application_name__)

"""
Reads/writes to the preferences DB.  All accesses to the DB are via this module.
"""


Base = sqlalchemy.ext.declarative.declarative_base()

PREFERENCES_FILE = 'preferences' + DB_EXTENSION


class KeyValueTable(Base):
    __tablename__ = 'keyvalue'

    key = sqlalchemy.Column(sqlalchemy.String(), primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.Boolean())
    datetime = sqlalchemy.Column(sqlalchemy.DateTime())


class PathsTable(Base):
    __tablename__ = 'paths'

    path = sqlalchemy.Column(sqlalchemy.String(), primary_key=True)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime())


class Preferences:

    def __init__(self, app_data_folder, init=False):

        self.__do_hidden_string = 'hidden'
        self.__do_system_string = 'system'
        self.__verbose_string = 'verbose'
        self.__background_monitor_string = 'monitor'

        if not app_data_folder:
            raise RuntimeError

        self.app_data_folder = app_data_folder
        os.makedirs(self.app_data_folder, exist_ok=True)
        self.__db_path = os.path.abspath(os.path.join(self.app_data_folder, PREFERENCES_FILE))
        self._sqlite_path = 'sqlite:///' + self.__db_path
        log.debug('preferences DB path : %s' % self._sqlite_path)
        self.__db_engine = sqlalchemy.create_engine(self._sqlite_path)  # , echo=True)
        if init:
            Base.metadata.create_all(self.__db_engine)
        self.__Session = sqlalchemy.orm.sessionmaker(bind=self.__db_engine)

    def get_db_path(self):
        return self._sqlite_path

    def _kv_set(self, key, value):
        log.debug('pref_set : %s to %s' % (str(key), str(value)))
        session = self.__Session()
        kv_table = KeyValueTable(key=key, value=value, datetime=datetime.datetime.utcnow())
        q = session.query(KeyValueTable).filter_by(key=key).first()
        if q:
            session.delete(q)
        session.add(kv_table)
        session.commit()
        session.close()

    def _kv_get(self, key):
        value = None
        session = self.__Session()
        try:
            row = session.query(KeyValueTable).filter_by(key=key).first()
        except sqlalchemy.exc.OperationalError as e:
            row = None
        if row:
            value = row.value
        session.close()
        log.debug('pref_get : %s = %s' % (str(key), str(value)))
        return value

    def set_do_hidden(self, value):
        self._kv_set(self.__do_hidden_string, bool(value))

    def get_do_hidden(self):
        return bool(self._kv_get(self.__do_hidden_string))

    def set_do_system(self, value):
        self._kv_set(self.__do_system_string, bool(value))

    def get_do_system(self):
        return bool(self._kv_get(self.__do_system_string))

    def set_verbose(self, value):
        self._kv_set(self.__verbose_string, bool(value))

    def get_verbose(self):
        return bool(self._kv_get(self.__verbose_string))

    def set_background_monitor(self, value):
        self._kv_set(self.__background_monitor_string, bool(value))

    def get_background_monitor(self):
        return bool(self._kv_get(self.__background_monitor_string))

    def add_path(self, path):
        session = self.__Session()
        session.add(PathsTable(path=path, datetime=datetime.datetime.utcnow()))
        session.commit()
        session.close()

    def remove_path(self, path):
        session = self.__Session()
        session.query(PathsTable).filter_by(path=path).delete()
        session.commit()
        session.close()

    def get_all_paths(self):
        session = self.__Session()
        paths = [row.path for row in session.query(PathsTable)]
        session.close()
        for path in paths:
            log.debug('get_all_paths : %s' % path)
        return paths

    def get_app_data_folder(self):
        return self.app_data_folder


def preferences_db_exists(folder):
    """
    Return True if preferences DB exists in the folder.
    :param folder: folder that (potentially) holds the preferences DB
    :return: True if DB found, False otherwise
    """
    try:
        return os.path.exists(os.path.join(folder, PREFERENCES_FILE))
    except TypeError:
        return False