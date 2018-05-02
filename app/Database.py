import configparser
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Database:
    db = None
    base = None

    def __init__(self):
        self.connect_to_db()

    def connect_to_db(self):
        engine = create_engine(self.build_db_conn_string(self.get_cfg()))

        self.base = declarative_base()
        Session = sessionmaker(bind=engine)
        self.db = Session()

    def build_db_conn_string(self, cfg):
        if cfg.has_section('database'):
            if cfg.get('database', 'system').lower() == 'sqlite':
                return "{system}:///{db}".format(**{
                    'system': os.environ.get('DB_SYSTEM') if None else cfg.get('database', 'system'),
                    'db': os.environ.get('DB_DATABASE') if None else cfg.get('database', 'database'),
               })

            return self.get_conn_string(cfg.get('database', 'system'), cfg.get('database', 'username'), cfg.get('database', 'password'), cfg.get('database', 'host'), cfg.get('database', 'database'),)
        else:
            return self.get_conn_string(os.environ.get('DB_SYSTEM'), os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'), os.environ.get('DB_HOST'), os.environ.get('DB_DATABASE'))

    @staticmethod
    def get_conn_string(system, username, password, host, database):
        return "{system}://{username}:{password}@{host}/{db}".format(**{
            'system': system,
            'username': username,
            'password': password,
            'host': host,
            'db': database,
        })

    @staticmethod
    def get_cfg():
        settings = configparser.ConfigParser()
        settings.read('settings.cfg')

        return settings


database = Database()
Base = database.base
Session = database.db

