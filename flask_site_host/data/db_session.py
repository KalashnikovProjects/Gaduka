import logging
from time import sleep

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from sqlalchemy.exc import OperationalError, StatementError
from sqlalchemy.orm.query import Query as _Query

import config

SqlAlchemyBase = dec.declarative_base()

__factory = None


# Для повторной попытки запроса
class RetryingQuery(_Query):
    __max_retry_count__ = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self):
        attempts = 0
        while True:
            attempts += 1
            try:
                return super().__iter__()
            except OperationalError as ex:
                if "server closed the connection unexpectedly" not in str(ex):
                    logging.error(f"Тотальная ошибка при запросе в базу данных {ex}.")
                    raise ex
                if attempts <= self.__max_retry_count__:
                    sleep_for = 2 ** (attempts - 1)
                    logging.warning(
                        f"Ошибка при запросе в базу данных {ex}. Попытка {attempts} из {self.__max_retry_count__}")
                    sleep(sleep_for)
                    continue
                else:
                    raise ex
            except StatementError as ex:
                logging.error(f"Тотальная ошибка при запросе в базу данных {ex}.")
                if "reconnect until invalid transaction is rolled back" not in str(ex):
                    raise ex
                self.session.rollback()


def global_init():
    global __factory

    if __factory:
        return
    logging.info(f"Подключение к базе данных по адресу {config.MYSQL_CONNECT_STRING}")

    engine = sa.create_engine(config.MYSQL_CONNECT_STRING, echo=False, connect_args={'charset': 'utf8mb4'},
                              pool_recycle=3600)
    __factory = orm.sessionmaker(bind=engine, query_cls=RetryingQuery)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
