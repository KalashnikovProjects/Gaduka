import os

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

import config

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return
    print(f"Подключение к базе данных по адресу {config.MYSQL_CONNECT_STRING}")

    engine = sa.create_engine(config.MYSQL_CONNECT_STRING, echo=False, connect_args={'charset': 'utf8mb4'}, pool_recycle=3600)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
